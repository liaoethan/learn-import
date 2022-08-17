import os
import re
import requests
import json
import logging
import hashlib


def getBreadcrumbElement(parent):
    link = parent["link"]
    title = parent["title"]
    return f'<a href="{link}">{title}</a>'


def getBreadcrumb(current_page_name, parents):
    breadcrumbs = map(getBreadcrumbElement, parents)
    return " &nbsp; / &nbsp;".join(breadcrumbs)


def importArticle(filepath, isRetryAttempt, config, authorization):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": authorization,
        "Content-Type": "application/json",
    }

    with open(filepath, encoding="utf-8") as f:
        article_data = json.load(f)

    sphinxOutputPathPrefix = filepath.split(config["SPHINX_OUTPUT_DIRECTORY"], 1)[-1]
    product = sphinxOutputPathPrefix.split(os.sep)[0]
    imagePrefix = (
        sphinxOutputPathPrefix.split(article_data["current_page_name"])[0] + "_images_"
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

    externalReferenceCode = hashlib.sha256(
        article_data["current_page_name"].encode()
    ).hexdigest()

    logger.info(
        f"Using ERC {externalReferenceCode} for {article_data['current_page_name']}"
    )

    article = {
        "contentFields": [
            {
                "contentFieldValue": {
                    "data": re.sub(
                        r'src="(\.\.\/)+_images/',
                        'src="' + config["WEBDAV_IMAGE_URL_PREFIX"] + imagePrefix,
                        article_data["body"],
                    )
                },
                "name": "Body",
            },
            {
                "contentFieldValue": {
                    "data": getBreadcrumb(
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
        "externalReferenceCode": externalReferenceCode,
        "friendlyUrlPath": product + "/" + article_data["current_page_name"] + ".html",
        "title": article_data["title"],
    }

    session = requests.Session()

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents/by-external-reference-code/{externalReferenceCode}"
    # post_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents"

    res = session.put(uri, headers=headers, data=json.dumps(article))

    if res.status_code == 403 and not isRetryAttempt:
        return False

    if not res.status_code == 200:
        errorMessage = f"Article import failed with return code: {res.status_code} and error message {json.dumps(res.json(), indent=4)}"
        logger.error(errorMessage)
        raise Exception(errorMessage)
    return True
