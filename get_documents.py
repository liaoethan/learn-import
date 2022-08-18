import get_all_items
import json
import logging
import requests


def get_documents(config, authorization):
    documents = get_all_items.get_all_items(config, authorization, get_document_batch)

    documents_by_title = {}
    for document in documents:
        documents_by_title[document["title"]] = document["id"]
    return documents_by_title


def get_document_batch(page, config, authorization):
    logger = logging.getLogger(__name__)

    headers = {
        "Accept": "application/json",
        "Authorization": authorization,
        "Content-Type": "application/json",
    }

    session = requests.Session()

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/documents?fields=id,title&page={page}&pageSize={config['API_PAGESIZE']}"
    logger.debug(f"Fetching document page {page}")
    res = session.get(get_uri, headers=headers)

    if res.status_code != 200:
        errorMessage = "Getting documents failed " + json.dumps(res.json(), indent=4)
        logger.error(errorMessage)
        raise Exception(errorMessage)
    return res.json()
