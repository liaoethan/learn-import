from configuration import config
from get_all_items import get_all_items
import json
import logging
import oauth_token
import requests
from document_rest import get_site_document_batch
from util import save_as_json
from jsonpath_ng.ext import parse


def get_liferay_document_paths_by_id(liferay_document_folders_by_path):

    liferay_document_paths_by_id = {}

    for path in liferay_document_folders_by_path:
        liferay_document_paths_by_id[
            liferay_document_folders_by_path[path]["id"]
        ] = path
    return liferay_document_paths_by_id


def get_liferay_site_documents_by_path(liferay_document_folders_by_path):

    liferay_document_paths_by_id = get_liferay_document_paths_by_id(
        liferay_document_folders_by_path
    )

    sha_256sum_jsonpath = parse(
        '$.documentType.contentFields[?(@.label=="sha_256sum")].contentFieldValue.data'
    )
    liferay_site_documents = get_all_items(get_site_document_batch)

    # Only consider documents that are of the Learn Synced Document Type
    liferay_site_learn_documents = filter(
        lambda site_document: site_document["documentType"]["name"]
        == config["DOCUMENT_TYPE"],
        liferay_site_documents,
    )

    liferay_site_documents_by_path = {}
    for liferay_site_document in liferay_site_learn_documents:

        sha_256sum_jsonpath_find_result = sha_256sum_jsonpath.find(
            liferay_site_document
        )
        sha_256sum = (
            sha_256sum_jsonpath_find_result[0].value
            if len(sha_256sum_jsonpath_find_result) == 1
            else ""
        )

        documentFolderId = liferay_site_document["documentFolderId"]
        path_key = (
            liferay_site_document["title"]
            if documentFolderId == 0
            else liferay_document_paths_by_id[liferay_site_document["documentFolderId"]]
            + "/"
            + liferay_site_document["title"]
        )
        liferay_site_documents_by_path[path_key] = {
            "documentFolderId": liferay_site_document["documentFolderId"],
            "id": liferay_site_document["id"],
            "sha_256sum": sha_256sum,
            "contentUrl": liferay_site_document["contentUrl"],
        }

    save_as_json("liferay_site_documents_by_path", liferay_site_documents_by_path)
    return liferay_site_documents_by_path
