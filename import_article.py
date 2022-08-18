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


def import_article(filepath, is_retry_attempt, config, authorization):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": authorization,
        "Content-Type": "application/json",
    }

    with open(filepath, encoding="utf-8") as f:
        article_data = json.load(f)

    sphinx_output_path_prefix = filepath.split(config["SPHINX_OUTPUT_DIRECTORY"], 1)[-1]
    product = sphinx_output_path_prefix.split(os.sep)[0]
    image_prefix = (
        sphinx_output_path_prefix.split(article_data["current_page_name"])[0]
        + "_images_"
    ).replace(os.sep, "_")

    if not "body" in article_data:
        logger.warn("No HTML body found for " + filepath)
        return True

    if not "parents" in article_data:
        article_data["parents"] = []

    if not "display_toc" in article_data:
        article_data["display_toc"] = False

    if not "navtoc" in article_data:
        article_data["navtoc"] = ""

    external_reference_code = hashlib.sha256(
        article_data["current_page_name"].encode()
    ).hexdigest()

    logger.info(
        f"Using ERC {external_reference_code} for {article_data['current_page_name']}"
    )

    article = {
        "contentFields": [
            {
                "contentFieldValue": {
                    "data": re.sub(
                        r'src="(\.\.\/)+_images/',
                        'src="' + config["WEBDAV_IMAGE_URL_PREFIX"] + image_prefix,
                        article_data["body"],
                    )
                },
                "name": "Body",
            },
            {
                "contentFieldValue": {
                    "data": get_breadcrumb(
                        article_data["current_page_name"], article_data["parents"]
                    )
                },
                "name": "Breadcrumb",
            },
            {
                "contentFieldValue": {
                    "data": article_data["toc"] if article_data["display_toc"] else ""
                },
                "name": "TOC",
            },
            {
                "contentFieldValue": {"data": article_data["navtoc"]},
                "name": "Navigation",
            },
        ],
        "contentStructureId": config["ARTICLE_STRUCTURE_ID"],
        "externalReferenceCode": external_reference_code,
        "friendlyUrlPath": product + "/" + article_data["current_page_name"] + ".html",
        "title": article_data["title"],
    }

    session = requests.Session()

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents/by-external-reference-code/{external_reference_code}"
    # post_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents"

    res = session.put(uri, headers=headers, data=json.dumps(article))

    if res.status_code == 403 and not is_retry_attempt:
        return False

    if not res.status_code == 200:
        error_message = f"Article import failed with return code: {res.status_code} and error message {json.dumps(res.json(), indent=4)}"
        logger.error(error_message)
        raise Exception(error_message)
    return True
