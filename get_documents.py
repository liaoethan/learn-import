from configuration import config
import get_all_items
import json
import logging
import oauth_token
import requests
from util import save_as_json
from jsonpath_ng.ext import parse


def get_documents():

    sha_256sum_jsonpath = parse(
        '$.documentType.contentFields[?(@.label=="sha_256sum")].contentFieldValue.data'
    )
    documents = get_all_items.get_all_items(get_document_batch)
    documents_by_title = {}
    for document in documents:

        sha_256sum_jsonpath_find_result = sha_256sum_jsonpath.find(document)
        sha_256sum = (
            sha_256sum_jsonpath_find_result[0].value
            if len(sha_256sum_jsonpath_find_result) == 1
            else ""
        )
        documents_by_title[document["title"]] = {
            "id": document["id"],
            "sha_256sum": sha_256sum,
        }

    save_as_json("documents_by_title", documents_by_title)
    return documents_by_title


@oauth_token.api_call(200)
def get_document_batch(page):
    logger = logging.getLogger(__name__)

    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/documents?fields=documentType,id,title&page={page}&pageSize={config['API_PAGESIZE']}"
    logger.info(f"Fetching document page {page}")
    return requests.get(get_uri, headers=headers)
