import requests
import json
import logging
import mimetypes


def importDocument(filepath, filename, documentsByTitle, config, authorization):
    logger = logging.getLogger(__name__)
    headers = {"Authorization": authorization}

    session = requests.Session()
    uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/documents"
    method = "POST"

    if filename in documentsByTitle:
        logger.info("Document already exists as id " + str(documentsByTitle[filename]))
        uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/documents/{documentsByTitle[filename]}"
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

    if not res.status_code == 200:
        errorMessage = "File import failed: " + json.dumps(res.json(), indent=4)
        logger.error(errorMessage)
        raise Exception(errorMessage)
