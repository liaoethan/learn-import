from configuration import config
from decorators import timer
import json
import logging
import logging.config
import mimetypes
import os
import oauth_token
import requests
import sys
from document_folder_rest import post_document_folder, get_document_folder_batch
from get_all_items import get_all_items
from util import save_as_json


@oauth_token.api_call(200)
def delete_file_entry(file_entry_id):

    logger = logging.getLogger(__name__)
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/dlfileentry"

    logger.debug(f"Using uri {uri}")
    method = "POST"

    data = {
        "method": "delete-file-entry",
        "params": {
            "fileEntryId": file_entry_id,
        },
        "id": 123,
        "jsonrpc": "2.0",
    }

    logger.info(f"Executing {json.dumps(data, indent=4)}")
    res = session.request(method, uri, headers=headers, data=json.dumps(data))

    response_payload = res.json()
    if "error" in response_payload:
        raise Exception(
            "Error invoking get-file-entries: " + response_payload["error"]["message"]
        )
    logger.debug(f"Response: {res.content}")
    return res


@oauth_token.api_call(200)
def get_file_entries(folder_id, start, end):
    logger = logging.getLogger(__name__)
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/dlfileentry"

    logger.debug(f"Using uri {uri}")
    method = "POST"

    data = {
        "method": "get-file-entries",
        "params": {
            "groupId": config["SITE_ID"],
            "folderId": folder_id,
            "start": start,
            "end": end,
            "-orderByComparator": "com.liferay.portlet.documentlibrary.util.comparator.DLFileEntryOrderByComparator",
        },
        "id": 123,
        "jsonrpc": "2.0",
    }

    logger.debug(f"Executing {json.dumps(data, indent=4)}")
    res = session.request(method, uri, headers=headers, data=json.dumps(data))

    response_payload = res.json()
    if "error" in response_payload:
        raise Exception(
            "Error invoking get-file-entries: " + response_payload["error"]["message"]
        )
    logger.debug(f"Response: {res.content}")
    return res


@timer
def delete_all_files():
    liferay_document_folders = get_all_items(get_document_folder_batch)
    for liferay_document_folder in liferay_document_folders:
        file_entries = get_file_entries(liferay_document_folder["id"], -1, -1).json()
        for file_entry in file_entries["result"]:
            print(f"{len(file_entries['result'])} in {liferay_document_folder['id']}")

            delete_file_entry(file_entry["fileEntryId"])
        save_as_json(f"get_entries_{liferay_document_folder['id']}", file_entries)


if __name__ == "__main__":
    delete_all_files()
