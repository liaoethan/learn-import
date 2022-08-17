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

config = configuration.getConfig()

logger.info(
    "Using host "
    + config["OAUTH_HOST"]
    + " and site "
    + config["SITE_ID"]
    + " and structureId "
    + str(config["ARTICLE_STRUCTURE_ID"])
)

session = requests.Session()


def importImages(authorization, documentsByTitle):
    importImageStart = time.perf_counter()
    fileCounter = 0
    for root, d_names, f_names in os.walk(config["SPHINX_OUTPUT_DIRECTORY"]):
        if root.endswith("_images"):
            for f in f_names:
                filename = str(os.path.join(root, f))
                importFilename = filename.split(config["SPHINX_OUTPUT_DIRECTORY"], 1)[
                    -1
                ].replace(os.sep, "_")
                logger.info(f"Importing... {filename} as {importFilename}")

                isRetryAttempt = False
                documentImportSuccess = False
                while not documentImportSuccess:
                    documentImportSuccess = import_document.importDocument(
                        filename,
                        importFilename,
                        documentsByTitle,
                        isRetryAttempt,
                        config,
                        authorization,
                    )
                    if not documentImportSuccess:
                        isRetryAttempt = True
                        authorization = oauth_token.getOAUTHToken(config)

                fileCounter = fileCounter + 1
                if fileCounter >= config["IMAGE_IMPORT_LIMIT"]:
                    logger.warning("Stopping import due to import limit being reached")
                    break

        if fileCounter >= config["IMAGE_IMPORT_LIMIT"]:
            break

    importImageEnd = time.perf_counter()
    logger.info(
        f"Imported {fileCounter} files in {importImageEnd - importImageStart:0.4f} seconds."
    )


def importArticles(authorization):
    importArticleStart = time.perf_counter()
    articleCounter = 0
    for root, d_names, f_names in os.walk(config["SPHINX_OUTPUT_DIRECTORY"]):
        for f in f_names:
            if f.endswith(LEARN_ARTICLE_JSON_EXTENSION):
                filename = os.path.join(root, f)
                logger.info("Importing... " + filename)

                isRetryAttempt = False
                importSuccess = False
                while not importSuccess:
                    importSuccess = import_article.importArticle(
                        filename, isRetryAttempt, config, authorization
                    )
                    if not importSuccess:
                        isRetryAttempt = True
                        authorization = oauth_token.getOAUTHToken(config)

                articleCounter = articleCounter + 1
                if articleCounter >= config["ARTICLE_IMPORT_LIMIT"]:
                    logger.warning("Stopping import due to import limit being reached")
                    break
        if articleCounter >= config["ARTICLE_IMPORT_LIMIT"]:
            break
    importArticleEnd = time.perf_counter()
    logger.info(
        f"Imported {articleCounter} articles in {importArticleEnd - importArticleStart:0.4f} seconds."
    )


importSuccess = False
importStart = time.perf_counter()
try:
    authorization = oauth_token.getOAUTHToken(config)
    documentsByTitle = get_documents.getDocuments(config, authorization)
    importImages(authorization, documentsByTitle)

    authorization = oauth_token.getOAUTHToken(config)
    articles = get_articles.getArticles(config, authorization)
    importArticles(authorization)

    importSuccess = True
except BaseException as err:
    logger.error(f"Unexpected {err=}, {type(err)=},  {traceback.format_exc()}")

importEnd = time.perf_counter()
logger.info(
    f"Learn import was {'successful' if importSuccess else 'NOT successful'} and completed in {importEnd - importStart:0.4f} seconds."
)
