import configuration
import get_articles
import get_documents
import import_article
import import_document
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

config = configuration.get_config()

logger.info(
    "Using host "
    + config["OAUTH_HOST"]
    + " and site "
    + config["SITE_ID"]
    + " and structureId "
    + str(config["ARTICLE_STRUCTURE_ID"])
)

session = requests.Session()


def import_images(authorization, documents_by_title):
    import_image_start = time.perf_counter()
    file_counter = 0
    for root, d_names, f_names in os.walk(config["SPHINX_OUTPUT_DIRECTORY"]):
        if root.endswith("_images"):
            for f in f_names:
                filename = str(os.path.join(root, f))
                import_filename = filename.split(config["SPHINX_OUTPUT_DIRECTORY"], 1)[
                    -1
                ].replace(os.sep, "_")
                logger.info(f"Importing... {filename} as {import_filename}")

                is_retry_attempt = False
                document_import_success = False
                while not document_import_success:
                    document_import_success = import_document.import_document(
                        filename,
                        import_filename,
                        documents_by_title,
                        is_retry_attempt,
                        config,
                        authorization,
                    )
                    if not document_import_success:
                        is_retry_attempt = True
                        authorization = oauth_token.get_oauth_token(config)

                file_counter = file_counter + 1
                if file_counter >= config["IMAGE_IMPORT_LIMIT"]:
                    logger.warning("Stopping import due to import limit being reached")
                    break

        if file_counter >= config["IMAGE_IMPORT_LIMIT"]:
            break

    import_image_end = time.perf_counter()
    logger.info(
        f"Imported {file_counter} files in {import_image_end - import_image_start:0.4f} seconds."
    )


def import_articles(authorization):
    import_article_start = time.perf_counter()
    article_counter = 0
    for root, d_names, f_names in os.walk(config["SPHINX_OUTPUT_DIRECTORY"]):
        for f in f_names:
            if f.endswith(LEARN_ARTICLE_JSON_EXTENSION):
                filename = os.path.join(root, f)
                logger.info("Importing... " + filename)

                is_retry_attempt = False
                import_success = False
                while not import_success:
                    import_success = import_article.import_article(
                        filename, is_retry_attempt, config, authorization
                    )
                    if not import_success:
                        is_retry_attempt = True
                        authorization = oauth_token.get_oauth_token(config)

                article_counter = article_counter + 1
                if article_counter >= config["ARTICLE_IMPORT_LIMIT"]:
                    logger.warning("Stopping import due to import limit being reached")
                    break
        if article_counter >= config["ARTICLE_IMPORT_LIMIT"]:
            break
    import_article_end = time.perf_counter()
    logger.info(
        f"Imported {article_counter} articles in {import_article_end - import_article_start:0.4f} seconds."
    )


import_success = False
import_start = time.perf_counter()
try:
    authorization = oauth_token.get_oauth_token(config)
    documents_by_title = get_documents.get_documents(config, authorization)
    import_images(authorization, documents_by_title)

    authorization = oauth_token.get_oauth_token(config)
    articles = get_articles.get_articles(config, authorization)
    import_articles(authorization)

    import_success = True
except BaseException as err:
    logger.error(f"Unexpected {err=}, {type(err)=},  {traceback.format_exc()}")

import_end = time.perf_counter()
logger.info(
    f"Learn import was {'successful' if import_success else 'NOT successful'} and completed in {import_end - import_start:0.4f} seconds."
)
