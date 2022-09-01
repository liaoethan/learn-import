from configuration import config
import requests
import json
import logging
import oauth_token


@oauth_token.api_call(200)
def get_data_definition_by_content_type_data_definition_key(
    content_type, data_definition_key
):
    uri = f"{config['OAUTH_HOST']}/o/data-engine/v2.0/sites/{config['SITE_ID']}/data-definitions/by-content-type/{content_type}/by-data-definition-key/{data_definition_key}"

    return requests.request(
        "GET",
        uri,
        headers={
            "Accept": "application/json",
            "Authorization": oauth_token.authorization,
            "Content-Type": "application/json",
        },
    )


@oauth_token.api_call(200)
def get_site_data_definition_by_content_type_page(page, content_type):
    logger = logging.getLogger(__name__)
    logger.info(f"Getting data definitions for page {page} content type {content_type}")

    uri = f"{config['OAUTH_HOST']}/o/data-engine/v2.0/sites/{config['SITE_ID']}/data-definitions/by-content-type/{content_type}?page={page}"

    return requests.request(
        "GET",
        uri,
        headers={
            "Accept": "application/json",
            "Authorization": oauth_token.authorization,
            "Content-Type": "application/json",
        },
    )


@oauth_token.api_call(200)
def post_site_data_definition_by_content_type(content_type, data_definition):
    logger = logging.getLogger(__name__)

    uri = f"{config['OAUTH_HOST']}/o/data-engine/v2.0/sites/{config['SITE_ID']}/data-definitions/by-content-type/{content_type}"

    return requests.request(
        "POST",
        uri,
        headers={
            "Accept": "application/json",
            "Authorization": oauth_token.authorization,
            "Content-Type": "application/json",
        },
        data=json.dumps(data_definition),
    )
