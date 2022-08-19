from configuration import config
import os
import re
import requests
import json
import logging
import hashlib


def get_breadcrumb_element(parent):
    link = parent["link"]
    title = parent["title"]
    return f'<a href="{link}">{title}</a>'


def get_breadcrumb(current_page_name, parents):
    breadcrumbs = map(get_breadcrumb_element, parents)
    return " &nbsp; / &nbsp;".join(breadcrumbs)


def import_article(article, is_retry_attempt, authorization):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": authorization,
        "Content-Type": "application/json",
    }
    translations = []

    contentFieldValues = {"body": {}, "breadcrumb": {}, "navtoc": {}, "toc": {}}

    for translation in article["translations"]:
        with open(translation["filename"], encoding="utf-8") as f:
            translation_data = json.load(f)

            if not "body" in translation_data:
                logger.warn("No HTML body found for " + translation["filename"])
                return True

            if not "parents" in translation_data:
                translation_data["parents"] = []

            if not "display_toc" in translation_data:
                translation_data["display_toc"] = False

            if not "navtoc" in translation_data:
                translation_data["navtoc"] = ""

            languages = {"en": "en-US", "ja": "ja-JP"}
            liferay_language_id = languages[translation["language"]]

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
        "contentFields": [
            {
                "contentFieldValue_i18n": contentFieldValues["body"],
                "name": "Body",
            },
            {
                "contentFieldValue_i18n": contentFieldValues["breadcrumb"],
                "name": "Breadcrumb",
            },
            {
                "contentFieldValue_i18n": contentFieldValues["toc"],
                "name": "TOC",
            },
            {
                "contentFieldValue_i18n": contentFieldValues["navtoc"],
                "name": "Navigation",
            },
        ],
        "contentStructureId": config["ARTICLE_STRUCTURE_ID"],
        "externalReferenceCode": external_reference_code,
        "friendlyUrlPath": f"{article['product']}/{translations[0]['current_page_name']}.html",
        "title": translations[0]["title"],
    }

    translation = article["translations"][0]
    languages = {"en": "en-US", "ja": "ja-JP"}
    liferay_language_id = languages[translation["language"]]

    untranslatedArticle = {
        "contentFields": [
            {
                "contentFieldValue": contentFieldValues["body"][liferay_language_id],
                "name": "Body",
            },
            {
                "contentFieldValue": contentFieldValues["breadcrumb"][
                    liferay_language_id
                ],
                "name": "Breadcrumb",
            },
            {
                "contentFieldValue": contentFieldValues["toc"][liferay_language_id],
                "name": "TOC",
            },
            {
                "contentFieldValue": contentFieldValues["navtoc"][liferay_language_id],
                "name": "Navigation",
            },
        ],
        "contentStructureId": config["ARTICLE_STRUCTURE_ID"],
        "externalReferenceCode": external_reference_code,
        "friendlyUrlPath": f"{article['product']}/{translations[0]['current_page_name']}.html",
        "title": translations[0]["title"],
    }

    save_as_json("article_request", untranslatedArticle)
    session = requests.Session()

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents/by-external-reference-code/{external_reference_code}"
    # post_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents"

    res = session.put(uri, headers=headers, data=json.dumps(untranslatedArticle))

    if res.status_code == 403 and not is_retry_attempt:
        return False

    if not res.status_code == 200:
        error_message = f"Article import failed with return code: {res.status_code} and error message {json.dumps(res.json(), indent=4)}"
        logger.error(error_message)
        raise Exception(error_message)
    return True


def save_as_json(name, object):
    BUILD_DIRECTORY = "build"
    if not os.path.isdir(BUILD_DIRECTORY):
        os.mkdir(BUILD_DIRECTORY)
    with open(f"{BUILD_DIRECTORY}/{name}.json", "w") as outfile:
        outfile.write(json.dumps(object, indent=4))
