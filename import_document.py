from configuration import config
import requests
import json
import logging
import oauth_token
import mimetypes


@oauth_token.api_call(200)
def import_document(filepath, filename, documents_by_title):
    logger = logging.getLogger(__name__)

    logger.info(f"Importing... {filepath} as {filename}")

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/documents"
    method = "POST"

    if filename in documents_by_title:
        logger.info(
            "Document already exists as id " + str(documents_by_title[filename])
        )
        uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/documents/{documents_by_title[filename]}"
        method = "PUT"

    image_type = mimetypes.guess_type(filepath)
    mime_type = image_type[0]
    if mime_type is None:
        raise Exception("Cannot determine mimetype for " + filepath)

    return requests.request(
        method,
        uri,
        headers={"Authorization": oauth_token.authorization},
        files=(
            (
                "document",
                (
                    None,
                    json.dumps({"title": filename, "externalReferenceCode": filename}),
                ),
            ),
            (
                "file",
                (filename, open(filepath, "rb"), str(mime_type)),
            ),
        ),
    )
