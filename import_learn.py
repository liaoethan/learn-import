from configuration import config
import get_articles
import get_documents
import import_article
import import_document
import json
import logging
import logging.config
import oauth_token
import os
import requests
import time
import traceback

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)

LEARN_ARTICLE_JSON_EXTENSION = ".fjson"

logger.info(
    "Using host "
    + config["OAUTH_HOST"]
    + " and site "
    + config["SITE_ID"]
    + " and structureId "
    + str(config["ARTICLE_STRUCTURE_ID"])
)

session = requests.Session()


def collect_sphinx_files():
    articles_by_article_key = {}
    images = []
    other = []
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
                    "image_prefix": f"{product}_{version}_{language}__images_",
                }
                if article_key not in articles_by_article_key:
                    articles_by_article_key[article_key] = {
                        "product": product,
                        "translations": [translation],
                    }
                else:
                    articles_by_article_key[article_key]["translations"].append(
                        translation
                    )
            elif root.endswith("_images"):
                images.append(
                    {
                        "filename": filename,
                        "import_filename": f"{product}_{version}_{language}_{'_'.join(subdirectories)}_{name}",
                        "product": product,
                        "version": version,
                        "language": language,
                    }
                )
            else:
                other.append(filename)

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
    save_as_json("images", images)
    save_as_json("other", other)

    return [articles, images, other]


def save_as_json(name, object):
    BUILD_DIRECTORY = "build"
    if not os.path.isdir(BUILD_DIRECTORY):
        os.mkdir(BUILD_DIRECTORY)
    with open(f"{BUILD_DIRECTORY}/{name}.json", "w") as outfile:
        outfile.write(json.dumps(object, indent=4))


def import_images(authorization, documents_by_title, images):
    import_image_start = time.perf_counter()
    file_counter = 0
    for image in images:
        is_retry_attempt = False
        document_import_success = False
        while not document_import_success:
            document_import_success = import_document.import_document(
                image["filename"],
                image["import_filename"],
                documents_by_title,
                is_retry_attempt,
                authorization,
            )
            if not document_import_success:
                is_retry_attempt = True
                authorization = oauth_token.get_oauth_token()

        file_counter = file_counter + 1
        if file_counter >= config["IMAGE_IMPORT_LIMIT"]:
            logger.warning("Stopping import due to import limit being reached")
            break

    import_image_end = time.perf_counter()
    logger.info(
        f"Imported {file_counter} files in {import_image_end - import_image_start:0.4f} seconds."
    )


def import_articles(articles, authorization):
    import_article_start = time.perf_counter()
    article_counter = 0
    for article in articles:
        logger.info(f"Importing... {article['article_key']}")
        is_retry_attempt = False
        import_success = False
        while not import_success:
            import_success = import_article.import_article(
                article, is_retry_attempt, authorization
            )
            if not import_success:
                is_retry_attempt = True
                authorization = oauth_token.get_oauth_token()

        article_counter = article_counter + 1
        if article_counter >= config["ARTICLE_IMPORT_LIMIT"]:
            logger.warning("Stopping import due to import limit being reached")
            break

    import_article_end = time.perf_counter()
    logger.info(
        f"Imported {article_counter} articles in {import_article_end - import_article_start:0.4f} seconds."
    )


import_success = False
import_start = time.perf_counter()
try:
    sphinx_articles, images, other = collect_sphinx_files()
    authorization = oauth_token.get_oauth_token()
    documents_by_title = get_documents.get_documents(authorization)
    import_images(authorization, documents_by_title, images)

    authorization = oauth_token.get_oauth_token()
    articles = get_articles.get_articles(authorization)
    import_articles(sphinx_articles, authorization)

    import_success = True
except BaseException as err:
    logger.error(f"Unexpected {err=}, {type(err)=},  {traceback.format_exc()}")

import_end = time.perf_counter()
logger.info(
    f"Learn import was {'successful' if import_success else 'NOT successful'} and completed in {import_end - import_start:0.4f} seconds."
)
