from configuration import config
import requests
import json
import logging
import oauth_token
import mimetypes


@oauth_token.api_call(200)
def import_document(filepath, filename, documents_by_title, sha_256sum):
    logger = logging.getLogger(__name__)

    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/documents"
    method = "POST"

    if filename in documents_by_title:

        document = documents_by_title[filename]

        logger.debug(
            f"Document {filename} already exists as id {document['id']} with sha_25sum {document['sha_256sum']}"
        )

        if sha_256sum == document["sha_256sum"]:
            logger.debug(f"Skipping document {filename} since sha_256sum value matches")
            return

        uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/documents/{document['id']}"
        method = "PUT"

    logger.info(f"Importing... {filepath} as {filename} with {method}")

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
                    json.dumps(
                        {
                            "title": filename,
                            "externalReferenceCode": filename,
                            "documentType": {
                                "contentFields": [
                                    {
                                        "contentFieldValue": {"data": sha_256sum},
                                        "name": "sha_256sum",
                                    }
                                ],
                                "name": "Learn Synced File",
                            },
                        }
                    ),
                ),
            ),
            (
                "file",
                (filename, open(filepath, "rb"), str(mime_type)),
            ),
        ),
    )
