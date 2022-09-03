from configuration import config
import requests
import json
import logging
import oauth_token
import mimetypes


@oauth_token.api_call(204)
def delete_document(documentId):
    logger = logging.getLogger(__name__)

    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/documents/{documentId}"
    logger.debug(f"Deleting document {documentId}")
    return requests.delete(uri, headers=headers)


@oauth_token.api_call(200)
def post_document_folder_document(
    local_file_path, title, documentFolderId, document_metadata
):

    return add_or_update_document(
        local_file_path,
        "POST",
        f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/document-folders/{documentFolderId}/documents",
        title,
        document_metadata,
    )


@oauth_token.api_call(200)
def put_document(local_file_path, title, documentId, document_metadata):
    return add_or_update_document(
        local_file_path,
        "PUT",
        f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/documents/{documentId}",
        title,
        document_metadata,
    )


@oauth_token.api_call(200)
def post_site_document(local_file_path, title, document_metadata):
    return add_or_update_document(
        local_file_path,
        "POST",
        f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/documents",
        title,
        document_metadata,
    )


def add_or_update_document(local_file_path, method, uri, title, document_metadata):

    image_type = mimetypes.guess_type(local_file_path)
    mime_type = image_type[0]
    if mime_type is None:
        raise Exception("Cannot determine mimetype for " + local_file_path)

    return requests.request(
        method,
        uri,
        headers={"Authorization": oauth_token.authorization},
        files=(
            (
                "document",
                (
                    None,
                    json.dumps(document_metadata),
                ),
            ),
            (
                "file",
                (title, open(local_file_path, "rb"), str(mime_type)),
            ),
        ),
    )


@oauth_token.api_call(200)
def get_site_document_batch(page):
    logger = logging.getLogger(__name__)

    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/documents?fields=contentUrl,documentFolderId,documentType,id,title&flatten=true&page={page}&pageSize={config['API_PAGESIZE']}"
    logger.info(f"Fetching document page {page}")
    return requests.get(get_uri, headers=headers)
