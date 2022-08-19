from configuration import config
import requests
import json
import logging
import mimetypes


def import_document(
    filepath, filename, documents_by_title, is_retry_attempt, authorization
):
    logger = logging.getLogger(__name__)
    headers = {"Authorization": authorization}

    session = requests.Session()
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
        raise Exception("cannot figure out mimetype for" + filepath)

    res = session.request(
        method,
        uri,
        headers=headers,
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

    if res.status_code == 403 and not is_retry_attempt:
        return False

    if not res.status_code == 200:
        error_message = f"File import failed with return code: {res.status_code} and error message {json.dumps(res.json(), indent=4)}"
        logger.error(error_message)
        raise Exception(error_message)

    return True
