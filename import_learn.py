from configuration import config
from decorators import timer
from util import save_as_json, sha_256sum
from document_folder import (
    add_missing_document_folders,
    get_liferay_document_folders_by_path,
)
from structured_content_folder import (
    add_missing_structured_content_folders,
    get_liferay_structured_content_folders_by_path,
)
from import_structured_contents import import_structured_contents
from import_documents import import_documents
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
    sphinx_article_paths = set()
    sphinx_document_paths = set()
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
                # Leave out language since we are consolidating translations into one article
                path = "/".join([product, version] + subdirectories)
                sphinx_article_paths.add(path)
                article_key = f"{product}_{version}_{'_'.join(subdirectories)}_{name}"

                translation = {
                    "language": language,
                    "filename": filename,
                    "image_prefix": f"{product}/{version}/{language}/{IMAGES_DIRECTORY}/",
                }
                if article_key not in articles_by_article_key:
                    articles_by_article_key[article_key] = {
                        "product": product,
                        "version": version,
                        "path": path,
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
                sphinx_document_paths.add(path)
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
    save_as_json("sphinx_document_paths", sorted(sphinx_document_paths))
    save_as_json("sphinx_article_paths", sorted(sphinx_article_paths))

    return [
        articles,
        sphinx_documents,
        sphinx_other_files,
        sorted(sphinx_document_paths),
        sorted(sphinx_article_paths),
    ]


def import_learn():
    import_success = False

    try:
        (
            sphinx_articles,
            sphinx_documents,
            sphinx_other_files,
            sphinx_document_paths,
            sphinx_article_paths,
        ) = collect_sphinx_files()

        (
            learn_article_data_definition,
            learn_synced_file_definition,
        ) = check_site_setup()
        liferay_document_folders_by_path = get_liferay_document_folders_by_path()

        add_missing_document_folders(
            sphinx_document_paths, liferay_document_folders_by_path
        )

        liferay_structured_content_folders_by_path = (
            get_liferay_structured_content_folders_by_path()
        )

        add_missing_structured_content_folders(
            sphinx_article_paths, liferay_structured_content_folders_by_path
        )

        liferay_site_documents_by_path = import_documents(
            sphinx_documents, liferay_document_folders_by_path
        )

        import_structured_contents(
            sphinx_articles,
            liferay_structured_content_folders_by_path,
            learn_article_data_definition["id"],
            liferay_site_documents_by_path,
        )

        import_success = True
    except BaseException as err:
        logger.error(f"Unexpected {err=}, {type(err)=}, {traceback.format_exc()}")

    logger.info(
        f"Learn import was {'successful' if import_success else 'NOT successful'}."
    )


import_learn()
