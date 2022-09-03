from configuration import config
from bs4 import BeautifulSoup
from util import sha_256sum_from_dictionary, save_as_json
from get_articles import get_liferay_site_structured_contents_by_friendlyurlpath
from liferay_api.structured_content_rest import (
    put_structured_content,
    post_structured_content_folder_structured_content,
    delete_structured_content,
)
from typing import List
import re
import requests
import json
import logging
from decorators import timer
import oauth_token
import hashlib
import os


def rename_readme(page_name):
    return re.sub(r"README", "index", page_name)


def get_breadcrumb_element(parent):
    link = rename_readme(parent["link"])
    title = parent["title"]
    return f'<a href="{link}">{title}</a>'


def get_breadcrumb(current_page_name, parents):
    breadcrumbs = map(get_breadcrumb_element, parents)
    return " &nbsp; / &nbsp;".join(breadcrumbs)


def get_structured_content_request_body(
    sphinx_article: dict, article_structure_id, liferay_site_documents_by_path
):
    logger = logging.getLogger(__name__)
    translations = []

    contentFieldValues = {
        "body": {},
        "breadcrumb": {},
        "navtoc": {},
        "toc": {},
        "sha_256sum": {},
        "github_edit_link": {},
    }
    title_i18n = {}
    available_languages = []

    for translation in sphinx_article["translations"]:
        with open(translation["filename"], encoding="utf-8") as f:
            translation_data = json.load(f)

            translation_data["current_page_name"] = rename_readme(
                translation_data["current_page_name"]
            )

            if not "body" in translation_data:
                logger.warn("No HTML body found for " + translation["filename"])
                return [{}, "", ""]

            if not "parents" in translation_data:
                translation_data["parents"] = []

            if not "display_toc" in translation_data:
                translation_data["display_toc"] = False

            if not "navtoc" in translation_data:
                translation_data["navtoc"] = ""

            if not "github_edit_link" in translation_data:
                subdirectories = ""

                if sphinx_article["subdirectories"]:
                    subdirectories = f"{'/'.join(sphinx_article['subdirectories'])}/"
                translation_data[
                    "github_edit_link"
                ] = f"{config['GITHUB_EDIT_LINK_BASE_URL']}{sphinx_article['product']}/{sphinx_article['version']}/{translation['language']}/{subdirectories}{os.path.splitext(sphinx_article['name'])[0] + '.md'}"

            languages = {"en": "en-US", "ja": "ja-JP"}
            liferay_language_id = languages[translation["language"]]
            title_i18n[liferay_language_id] = translation_data["title"]
            # if title is not set for default language id we get an error
            title_i18n[config["DEFAULT_LANGUAGE_ID"]] = translation_data["title"]
            available_languages.append(liferay_language_id)

            soup_body = BeautifulSoup(translation_data["body"], features="html.parser")
            for img in soup_body.findAll("img"):
                img_src = img.get("src")
                regex_pattern = re.compile(r"(\.\.\/)*_images/(.*)")
                matches = regex_pattern.match(img_src)
                if matches == None:
                    logger.warn(
                        f"No match found in img {img_src} in article {translation_data['current_page_name']}"
                    )
                    continue

                image_file_name = matches.group(2)
                document_path = translation["image_prefix"] + image_file_name
                img["src"] = liferay_site_documents_by_path[document_path]["contentUrl"]
                logger.debug(
                    f"Updating {img_src} to {liferay_site_documents_by_path[document_path]['contentUrl']}"
                )

            contentFieldValues["body"][liferay_language_id] = {"data": str(soup_body)}

            contentFieldValues["breadcrumb"][liferay_language_id] = {
                "data": get_breadcrumb(
                    translation_data["current_page_name"],
                    translation_data["parents"],
                )
            }

            contentFieldValues["toc"][liferay_language_id] = {
                "data": translation_data["toc"]
                if translation_data["display_toc"]
                else ""
            }

            contentFieldValues["navtoc"][liferay_language_id] = {
                "data": translation_data["navtoc"]
            }

            contentFieldValues["github_edit_link"][liferay_language_id] = {
                "data": translation_data["github_edit_link"]
            }

            translations.append(translation_data)

    if config["DEFAULT_LANGUAGE_ID"] not in available_languages:
        available_languages.append(config["DEFAULT_LANGUAGE_ID"])

    # make sure all languages have at least an empty data section
    for liferay_language_id in available_languages:
        for key in contentFieldValues:
            if liferay_language_id not in contentFieldValues[key]:
                contentFieldValues[key][liferay_language_id] = {"data": ""}

    # friendlyUrlPaths are all lower case (otherwise Liferay will modify it)
    friendly_url_path = f"{sphinx_article['product']}/{sphinx_article['version']}/{translations[0]['current_page_name'].lower()}.html"

    structured_content_request_body = {
        "availableLanguages": available_languages,
        "contentFields": [
            {
                "contentFieldValue": {"data": ""},
                "contentFieldValue_i18n": contentFieldValues["body"],
                "name": "Body",
            },
            {
                "contentFieldValue": {"data": ""},
                "contentFieldValue_i18n": contentFieldValues["breadcrumb"],
                "name": "Breadcrumb",
            },
            {
                "contentFieldValue": {"data": ""},
                "contentFieldValue_i18n": contentFieldValues["toc"],
                "name": "TOC",
            },
            {
                "contentFieldValue": {"data": ""},
                "contentFieldValue_i18n": contentFieldValues["navtoc"],
                "name": "Navigation",
            },
            {
                "contentFieldValue": {"data": ""},
                "contentFieldValue_i18n": contentFieldValues["github_edit_link"],
                "name": "githubEditLink",
            },
        ],
        "contentStructureId": article_structure_id,
        # CAREFUL here - sometimes friendlyURLs are based on title unless the fields are setup correctly
        "friendlyUrlPath": "",
        "friendlyUrlPath_i18n": {
            liferay_language_id: friendly_url_path
            for liferay_language_id in available_languages
        },
        "title_i18n": title_i18n,
        "title": translations[0]["title"],
        "viewableBy": "Anyone",
    }

    sha_256sum = sha_256sum_from_dictionary(structured_content_request_body)

    structured_content_request_body["contentFields"].append(
        {
            "contentFieldValue": {"data": ""},
            "contentFieldValue_i18n": {
                liferay_language_id: {"data": sha_256sum}
                for liferay_language_id in available_languages
            },
            "name": "sha_256sum",
        }
    )

    return [
        structured_content_request_body,
        sha_256sum,
        friendly_url_path,
    ]


@timer
def import_structured_contents(
    sphinx_articles,
    liferay_structured_content_folders_by_path,
    article_structure_id,
    liferay_site_documents_by_path,
):

    liferay_site_structured_contents_by_friendlyurlpath = (
        get_liferay_site_structured_contents_by_friendlyurlpath(article_structure_id)
    )

    logger = logging.getLogger(__name__)
    article_counter = 0
    unchanged_article_count = 0
    updated_article_count = 0
    new_article_count = 0
    empty_article_count = 0

    for sphinx_article in sphinx_articles:
        (
            structured_content_request_body,
            sha_256sum,
            friendly_url_path,
        ) = get_structured_content_request_body(
            sphinx_article, article_structure_id, liferay_site_documents_by_path
        )

        save_as_json("structured_content_request_body", structured_content_request_body)

        if len(structured_content_request_body) == 0:
            empty_article_count = empty_article_count + 1
        elif friendly_url_path in liferay_site_structured_contents_by_friendlyurlpath:
            liferay_site_structured_content = (
                liferay_site_structured_contents_by_friendlyurlpath[friendly_url_path]
            )
            if liferay_site_structured_content["sha_256sum"] == sha_256sum:
                logger.debug(
                    f"Skipping due to sha match {sphinx_article['article_key']}"
                )
                unchanged_article_count = unchanged_article_count + 1
                liferay_site_structured_content["status"] = "unchanged"
            else:
                logger.info(f"Updating existing {friendly_url_path}")
                liferay_site_structured_content["status"] = "updated"
                updated_article_count = updated_article_count + 1
                put_structured_content(
                    liferay_site_structured_content["id"],
                    structured_content_request_body,
                )
        else:
            structuredContentFolderId = (
                liferay_structured_content_folders_by_path[sphinx_article["path"]]["id"]
                if sphinx_article["path"] in liferay_structured_content_folders_by_path
                else 0
            )

            logger.info(
                f"Adding new {friendly_url_path} in folder {structuredContentFolderId}"
            )

            post_structured_content_folder_structured_content(
                structuredContentFolderId,
                structured_content_request_body,
            )
            new_article_count = new_article_count + 1

        article_counter = article_counter + 1
        if (
            config["STRUCTURED_CONTENT_IMPORT_LIMIT"] > 0
            and article_counter >= config["STRUCTURED_CONTENT_IMPORT_LIMIT"]
        ):
            logger.warning(
                f"Stopping structured content import due to import limit being reached {config['STRUCTURED_CONTENT_IMPORT_LIMIT']}"
            )
            break

    logger.info(
        f"Processed {article_counter} sphinx articles: {new_article_count} new articles, {updated_article_count} updated articles, {unchanged_article_count} unchanged articles, {empty_article_count} empty articles"
    )
    delete_count = 0
    for friendlyurlpath in liferay_site_structured_contents_by_friendlyurlpath:
        liferay_site_structured_content = (
            liferay_site_structured_contents_by_friendlyurlpath[friendlyurlpath]
        )
        if not "status" in liferay_site_structured_content:
            logger.info(f"Deleting non-sphinx article: {friendlyurlpath}")
            delete_structured_content(liferay_site_structured_content["id"])
            delete_count = delete_count + 1
    logger.info(f"Deleted {delete_count} non-sphinx structured contents")
