from configuration import config
import get_all_items
import json
import logging
import oauth_token
import requests
import util


@oauth_token.api_call(200)
def get_site_structured_contents_page(page):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
        "Accept-Language": config["DEFAULT_LANGUAGE_ID"],
    }

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents?fields=key,contentFields,id,friendlyUrlPath,contentStructureId,structuredContentFolderId&flatten=true&page={page}&pageSize={config['API_PAGESIZE']}"

    logger.info(f"Fetching structured contents page {page}")
    return requests.get(get_uri, headers=headers)


@oauth_token.api_call(204)
def delete_structured_content(structuredContentId):

    return requests.delete(
        f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/structured-contents/{structuredContentId}",
        headers={
            "Accept": "application/json",
            "Authorization": oauth_token.authorization,
            "Content-Type": "application/json",
        },
    )


@oauth_token.api_call(200)
def post_structured_content_folder_structured_content(
    structuredContentFolderId, structuredContent
):
    return add_or_update_structured_content(
        f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/structured-content-folders/{structuredContentFolderId}/structured-contents",
        "POST",
        structuredContent,
    )


@oauth_token.api_call(200)
def put_structured_content(structuredContentId, structuredContent):
    return add_or_update_structured_content(
        f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/structured-contents/{structuredContentId}",
        "PUT",
        structuredContent,
    )


def add_or_update_structured_content(uri, method, structuredContent):
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    res = session.request(
        method, uri, headers=headers, data=json.dumps(structuredContent)
    )

    json_res = res.json()

    requested_friendly_url_path = structuredContent["title"]
    if "friendlyUrlPath" in json_res:
        response_friendly_url_path = json_res["friendlyUrlPath"]
        if response_friendly_url_path != requested_friendly_url_path:
            raise Exception(
                f"Different friendlyUrlPath created: {response_friendly_url_path}, requested {requested_friendly_url_path}"
            )

    return res
