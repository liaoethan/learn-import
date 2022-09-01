from configuration import config
from util import save_as_json
import re
import requests
import json
import logging
import oauth_token


@oauth_token.api_call(200)
def import_article(structureId):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    external_reference_code = "asdasdasdadsad"
    translatedArticle = {
        "availableLanguages": ["en-US", "ja-JP"],
        "contentFields": [
            {
                "contentFieldValue": {"data": "Lorem lacinia sed amet culpa integer"},
                "contentFieldValue_i18n": {
                    "en-US": {"data": "english"},
                    "ja-JP": {"data": "japanese"},
                },
                "name": "Body",
            },
            {
                "contentFieldValue": {"data": "Lorem lacinia sed amet culpa integer"},
                "contentFieldValue_i18n": {
                    "en-US": {"data": "english"},
                    "ja-JP": {"data": "japanese"},
                },
                "name": "TOC",
            },
            {
                "contentFieldValue": {"data": "Lorem lacinia sed amet culpa integer"},
                "contentFieldValue_i18n": {
                    "en-US": {"data": "english"},
                    "ja-JP": {"data": "japanese"},
                },
                "name": "Breadcrumb",
            },
            {
                "contentFieldValue": {"data": "Lorem lacinia sed amet culpa integer"},
                "contentFieldValue_i18n": {
                    "en-US": {"data": "english"},
                    "ja-JP": {"data": "japanese"},
                },
                "name": "Navigation",
            },
        ],
        "title_i18n": {"en-US": "This is my content", "ja-JP": "japanese content"},
        "contentStructureId": structureId,
        "externalReferenceCode": external_reference_code,
        "friendlyUrlPath": f"thisisatest",
        "title": "thisisatest",
    }

    save_as_json("article_request", translatedArticle)
    session = requests.Session()

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents"
    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents/by-external-reference-code/{external_reference_code}"
    method = "POST"
    method = "PUT"

    res = session.request(
        method, uri, headers=headers, data=json.dumps(translatedArticle)
    )
    print(json.dumps(res.json(), indent=4))
    return res


# import_article(85718)
