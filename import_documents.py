from get_documents import get_liferay_site_documents_by_path
from decorators import timer
from document_rest import (
    delete_document,
    post_site_document,
    put_document,
    post_document_folder_document,
    delete_document,
)
from configuration import config
import logging


@timer
def delete_documents(liferay_site_documents_by_path):
    logger = logging.getLogger(__name__)

    delete_count = 0
    for path in liferay_site_documents_by_path:
        liferay_site_document = liferay_site_documents_by_path[path]
        if not "sphinx_document_status" in liferay_site_document:
            logger.info(f"Deleting non-sphinx document: {path}")
            delete_document(liferay_site_document["id"])
            delete_count = delete_count + 1
    logger.info(f"Deleted {delete_count} non-sphinx documents")


@timer
def import_documents(sphinx_documents, liferay_document_folders_by_path):
    logger = logging.getLogger(__name__)

    liferay_site_documents_by_path = get_liferay_site_documents_by_path(
        liferay_document_folders_by_path
    )
    document_counter = 0
    unchanged_document_count = 0
    updated_document_count = 0
    new_document_count = 0
    for sphinx_document in sphinx_documents:

        documentFolderId = (
            liferay_document_folders_by_path[sphinx_document["path"]]["id"]
            if sphinx_document["path"] in liferay_document_folders_by_path
            else 0
        )
        document_path = sphinx_document["document_path"]
        title = sphinx_document["title"]
        local_file_path = sphinx_document["local_file_path"]
        sha_256sum = sphinx_document["sha_256sum"]

        document_metadata = {
            "title": title,
            "documentFolderId": documentFolderId,
            "documentType": {
                "contentFields": [
                    {
                        "contentFieldValue": {"data": sha_256sum},
                        "name": "sha_256sum",
                    }
                ],
                "name": config["DOCUMENT_TYPE"],
            },
            "viewableBy": "Anyone",
        }

        # Check if document already exists in liferay
        if document_path in liferay_site_documents_by_path:

            liferay_site_document = liferay_site_documents_by_path[document_path]

            logger.debug(
                f"Document {title} already exists as id {liferay_site_document['id']} with sha_25sum {liferay_site_document['sha_256sum']}"
            )

            if sha_256sum != liferay_site_document["sha_256sum"]:
                logger.info(f"Updating {document_path}")
                put_document(
                    local_file_path,
                    title,
                    liferay_site_document["id"],
                    document_metadata,
                )
                liferay_site_document["sphinx_document_status"] = "updated"
                updated_document_count = updated_document_count + 1

            else:
                liferay_site_document["sphinx_document_status"] = "unchanged"
                unchanged_document_count = unchanged_document_count + 1
                logger.debug(
                    f"Skipping document {title} since sha_256sum value matches"
                )

        elif documentFolderId != 0:
            logger.info(
                f"Adding new document {document_path} in folder {documentFolderId}"
            )
            post_document_folder_document(
                local_file_path, title, documentFolderId, document_metadata
            )

            new_document_count = new_document_count + 1
        else:
            logger.info(f"Adding new document {document_path} in root folder")
            post_site_document(local_file_path, title, document_metadata)
            new_document_count = new_document_count + 1

        document_counter = document_counter + 1
        if (
            config["DOCUMENT_IMPORT_LIMIT"] > 0
            and document_counter >= config["DOCUMENT_IMPORT_LIMIT"]
        ):
            logger.warning(
                f"Stopping import due to import limit being reached {config['DOCUMENT_IMPORT_LIMIT']}!"
            )
            break
    logger.info(
        f"Processed {document_counter} sphinx_documents: {new_document_count} new documents, {updated_document_count} updated documents, {unchanged_document_count} unchanged documents"
    )

    delete_documents(liferay_site_documents_by_path)
