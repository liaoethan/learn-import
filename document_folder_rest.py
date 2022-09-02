from configuration import config
import get_all_items
import json
import logging
import oauth_token
import requests
import util


@oauth_token.api_call(200)
def get_document_folder_batch(page):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/document-folders?fields=id,parentDocumentFolderId,name&flatten=true&page={page}&pageSize={config['API_PAGESIZE']}"

    logger.info(f"Fetching document folder page {page}")
    return requests.get(get_uri, headers=headers)


@oauth_token.api_call(200)
def post_document_folder(name, parentDocumentFolderId):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/document-folders"

    if parentDocumentFolderId != 0:
        uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/document-folders/{parentDocumentFolderId}/document-folders"

    logger.debug(
        f"Creating document folder {name} for parentDocumentFolderId {parentDocumentFolderId}"
    )
    return requests.post(
        uri,
        headers=headers,
        data=json.dumps(
            {
                "name": name,
                "parentDocumentFolderId": parentDocumentFolderId,
                "viewableBy": "Anyone",
            }
        ),
    )
