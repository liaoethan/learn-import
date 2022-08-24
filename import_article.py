from configuration import config
from util import sha_256sum_from_dictionary, save_as_json
import re
import requests
import json
import logging
import oauth_token
import hashlib


def get_breadcrumb_element(parent):
    link = parent["link"]
    title = parent["title"]
    return f'<a href="{link}">{title}</a>'


def get_breadcrumb(current_page_name, parents):
    breadcrumbs = map(get_breadcrumb_element, parents)
    return " &nbsp; / &nbsp;".join(breadcrumbs)


@oauth_token.api_call(200)
def import_article(article, articles_by_friendlyurlpath):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }
    translations = []

    contentFieldValues = {
        "body": {},
        "breadcrumb": {},
        "navtoc": {},
        "toc": {},
        "sha_256sum": {},
    }
    title_i18n = {}
    available_languages = []

    for translation in article["translations"]:
        with open(translation["filename"], encoding="utf-8") as f:
            translation_data = json.load(f)

            if not "body" in translation_data:
                logger.warn("No HTML body found for " + translation["filename"])
                return

            if not "parents" in translation_data:
                translation_data["parents"] = []

            if not "display_toc" in translation_data:
                translation_data["display_toc"] = False

            if not "navtoc" in translation_data:
                translation_data["navtoc"] = ""

            languages = {"en": "en-US", "ja": "ja-JP"}
            liferay_language_id = languages[translation["language"]]
            title_i18n[liferay_language_id] = translation_data["title"]
            available_languages.append(liferay_language_id)

            contentFieldValues["body"][liferay_language_id] = {
                "data": re.sub(
                    r'src="(\.\.\/)+_images/',
                    'src="'
                    + config["WEBDAV_IMAGE_URL_PREFIX"]
                    + translation["image_prefix"],
                    translation_data["body"],
                )
            }

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

            translations.append(translation_data)

    external_reference_code = hashlib.sha256(
        article["article_key"].encode()
    ).hexdigest()

    translatedArticle = {
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
        ],
        "contentStructureId": config["ARTICLE_STRUCTURE_ID"],
        "externalReferenceCode": external_reference_code,
        # friendlyUrlPaths are all lower case (otherwise Liferay will modify it)
        "friendlyUrlPath": f"{article['product']}/{translations[0]['current_page_name'].lower()}.html",
        "title_i18n": title_i18n,
        "title": translations[0]["current_page_name"],
    }

    sha_256sum = sha_256sum_from_dictionary(translatedArticle)

    if translatedArticle["friendlyUrlPath"] in articles_by_friendlyurlpath:
        liferay_article = articles_by_friendlyurlpath[
            translatedArticle["friendlyUrlPath"]
        ]
        if liferay_article["sha_256sum"] == sha_256sum:
            logger.debug(f"Skipping due to sha match {article['article_key']}")
            return
        else:
            logger.info(
                f"Importing... {article['article_key']} since {liferay_article['sha_256sum']} does not match {sha_256sum} "
            )
    else:
        logger.info(
            f"Did not find {translatedArticle['friendlyUrlPath']} in existing articles"
        )

    logger.info(f"Importing... {article['article_key']}")

    # Make sure the default language has the sha value since it's what's returned in get_articles
    DEFAULT_LANGUAGE_ID = "en-US"

    translatedArticle["contentFields"].append(
        {
            "contentFieldValue": {"data": ""},
            "contentFieldValue_i18n": {DEFAULT_LANGUAGE_ID: {"data": sha_256sum}},
            "name": "sha_256sum",
        }
    )

    save_as_json("article_request", translatedArticle)
    session = requests.Session()

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents/by-external-reference-code/{external_reference_code}"
    # post_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents"

    return session.put(uri, headers=headers, data=json.dumps(translatedArticle))
