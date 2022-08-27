from configuration import config
import get_all_items
import json
import logging
import oauth_token
import requests
import util


@oauth_token.api_call(200)
def get_structured_content_folder_batch(page):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-content-folders?fields=id,parentStructuredContentFolderId,name&flatten=true&page={page}&pageSize={config['API_PAGESIZE']}"

    logger.info(f"Fetching structured content folder page {page}")
    return requests.get(get_uri, headers=headers)


@oauth_token.api_call(200)
def post_structured_content_folder(name, parentStructuredContentFolderId):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-content-folders"

    if parentStructuredContentFolderId != 0:
        uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/structured-content-folders/{parentStructuredContentFolderId}/structured-content-folders"

    logger.debug(
        f"Creating structured content folder {name} for parentStructuredContentFolderId {parentStructuredContentFolderId}"
    )
    return requests.post(
        uri,
        headers=headers,
        data=json.dumps(
            {
                "name": name,
                "parentStructuredContentFolderId": parentStructuredContentFolderId,
            }
        ),
    )
