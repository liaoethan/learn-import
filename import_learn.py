from configuration import config
from decorators import timer
from util import save_as_json, sha_256sum
import get_articles
from get_documents import get_liferay_site_documents_by_path
from document_folder import (
    add_missing_document_folders,
    get_liferay_document_folders_by_path,
)
import import_article
from document_rest import (
    delete_document,
    post_site_document,
    put_document,
    post_document_folder_document,
    delete_document,
)
from site_setup import check_site_setup
import json
import logging
import os
import requests
import traceback


logger = logging.getLogger(__name__)

LEARN_ARTICLE_JSON_EXTENSION = ".fjson"
IMAGES_DIRECTORY = "_images"
session = requests.Session()


@timer
def collect_sphinx_files():
    articles_by_article_key = {}
    document_paths = set()
    sphinx_documents = []
    sphinx_other_files = []
    for root, d_names, f_names in os.walk(config["SPHINX_OUTPUT_DIRECTORY"]):
        for f in f_names:
            filename = str(os.path.join(root, f))
            # Sample path - /home/allenz/liferay/liferay-learn/site/build/output/commerce/latest/en/search.fjson
            # Get the sphinx relevant part of the path into sphinx_output_path, i.e. commerce/latest/en/search.fjson
            _, sphinx_output_path = filename.split(config["SPHINX_OUTPUT_DIRECTORY"])

            if sphinx_output_path.startswith("homepage"):
                (product, *subdirectories, name) = sphinx_output_path.split(os.sep)
                version = "latest"
                language = "en"
            else:
                (
                    product,
                    version,
                    language,
                    *subdirectories,
                    name,
                ) = sphinx_output_path.split(os.sep)

            if filename.endswith(LEARN_ARTICLE_JSON_EXTENSION):
                article_key = f"{product}_{version}_{'_'.join(subdirectories)}_{name}"

                translation = {
                    "language": language,
                    "filename": filename,
                    "image_prefix": f"{product}/{version}/{language}/{IMAGES_DIRECTORY}/",
                }
                if article_key not in articles_by_article_key:
                    articles_by_article_key[article_key] = {
                        "product": product,
                        "translations": [translation],
                        "version": version,
                        "subdirectories": subdirectories,
                        "name": name,
                    }
                else:
                    articles_by_article_key[article_key]["translations"].append(
                        translation
                    )
            elif root.endswith(IMAGES_DIRECTORY) or filename.endswith(".zip"):
                path = "/".join([product, version, language] + subdirectories)
                document_paths.add(path)
                sphinx_documents.append(
                    {
                        "local_file_path": filename,
                        "title": name,
                        "path": path,
                        "document_path": path + "/" + name,
                        "product": product,
                        "version": version,
                        "language": language,
                        "sha_256sum": sha_256sum(filename),
                    }
                )
            else:
                sphinx_other_files.append(filename)

    articles = []
    for article_by_article_key in articles_by_article_key:
        articles.append(
            {
                "article_key": article_by_article_key,
                **articles_by_article_key[article_by_article_key],
            }
        )

    save_as_json("articles_by_article_key", articles_by_article_key)
    save_as_json("articles", articles)
    save_as_json("sphinx_documents", sphinx_documents)
    save_as_json("sphinx_other_files", sphinx_other_files)
    save_as_json("document_paths", sorted(document_paths))

    return [articles, sphinx_documents, sphinx_other_files, sorted(document_paths)]


@timer
def delete_documents(liferay_site_documents_by_path):
    delete_count = 0
    for path in liferay_site_documents_by_path:
        liferay_site_document = liferay_site_documents_by_path[path]
        if not "sphinx_document_status" in liferay_site_document:
            logger.info(f"Deleting non-sphinx document: {path}")
            delete_document(liferay_site_document["id"])
            delete_count = delete_count + 1
    logger.info(f"Deleted {delete_count} non-sphinx documents")


@timer
def import_documents(
    liferay_site_documents_by_path, sphinx_documents, liferay_document_folders_by_path
):
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


@timer
def import_articles(articles, articles_by_friendlyurlpath, article_structure_id):
    article_counter = 0
    for article in articles:
        import_article.import_article(
            article, articles_by_friendlyurlpath, article_structure_id
        )

        article_counter = article_counter + 1
        if (
            config["ARTICLE_IMPORT_LIMIT"] > 0
            and article_counter >= config["ARTICLE_IMPORT_LIMIT"]
        ):
            logger.warning(
                f"Stopping article import due to import limit being reached {config['ARTICLE_IMPORT_LIMIT']}"
            )
            break

    logger.info(f"Imported {article_counter} articles.")


@timer
def import_learn():
    import_success = False

    try:
        (
            sphinx_articles,
            sphinx_documents,
            sphinx_other_files,
            sphinx_document_paths,
        ) = collect_sphinx_files()

        (
            learn_article_data_definition,
            learn_synced_file_definition,
        ) = check_site_setup()
        liferay_document_folders_by_path = get_liferay_document_folders_by_path()

        add_missing_document_folders(
            sphinx_document_paths, liferay_document_folders_by_path
        )
        liferay_site_documents_by_path = get_liferay_site_documents_by_path(
            liferay_document_folders_by_path
        )
        import_documents(
            liferay_site_documents_by_path,
            sphinx_documents,
            liferay_document_folders_by_path,
        )
        delete_documents(liferay_site_documents_by_path)
        save_as_json(
            "updated_liferay_site_documents_by_path", liferay_site_documents_by_path
        )
        articles_by_friendlyurlpath = get_articles.get_articles()
        import_articles(
            sphinx_articles,
            articles_by_friendlyurlpath,
            learn_article_data_definition["id"],
        )

        import_success = True
    except BaseException as err:
        logger.error(f"Unexpected {err=}, {type(err)=}, {traceback.format_exc()}")

    logger.info(
        f"Learn import was {'successful' if import_success else 'NOT successful'}."
    )


import_learn()
