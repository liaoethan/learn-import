from configuration import config
import get_all_items
import json
import logging
import oauth_token
import requests


def get_documents():
    documents = get_all_items.get_all_items(get_document_batch)

    documents_by_title = {}
    for document in documents:
        documents_by_title[document["title"]] = document["id"]
    return documents_by_title


@oauth_token.api_call(200)
def get_document_batch(page):
    logger = logging.getLogger(__name__)

    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/documents?fields=id,title&page={page}&pageSize={config['API_PAGESIZE']}"
    logger.debug(f"Fetching document page {page}")
    return requests.get(get_uri, headers=headers)
