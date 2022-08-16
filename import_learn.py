import configuration
import get_articles
import import_article
import import_file
import logging
import logging.config
import oauth_token
import os
import requests
import time

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

authorization = oauth_token.getOAUTHToken(config)

session = requests.Session()


def importImages():
    importImageStart = time.perf_counter()
    fileCounter = 0
    for root, d_names, f_names in os.walk(config["SPHINX_OUTPUT_DIRECTORY"]):
        if root.endswith("_images"):
            for f in f_names:
                filename = os.path.join(root, f)
                logger.info("Importing... " + filename)
                import_file.importFile(filename, "commerce_" + f, config, authorization)
                fileCounter = fileCounter + 1

    importImageEnd = time.perf_counter()
    logger.info(
        f"Imported {fileCounter} files in {importImageEnd - importImageStart:0.4f} seconds."
    )


def importArticles():
    importArticleStart = time.perf_counter()
    articleCounter = 0
    for root, d_names, f_names in os.walk(config["SPHINX_OUTPUT_DIRECTORY"]):
        for f in f_names:
            if f.endswith(LEARN_ARTICLE_JSON_EXTENSION):
                filename = os.path.join(root, f)
                logger.info("Importing... " + filename)
                import_article.importArticle(filename, config, authorization)
                articleCounter = articleCounter + 1
    importArticleEnd = time.perf_counter()
    logger.info(
        f"Imported {articleCounter} articles in {importArticleEnd - importArticleStart:0.4f} seconds."
    )


importSuccess = False
importStart = time.perf_counter()
try:
    # importImages()
    # articles = get_articles.getArticles(config, authorization)
    # logger.debug(json.dumps(articles, indent=4))
    importArticles()
    importSuccess = True
except BaseException as err:
    print(f"Unexpected {err=}, {type(err)=}")

importEnd = time.perf_counter()
logger.info(
    f"Learn import was {'successful' if importSuccess else 'NOT successful'} and completed in  {importEnd - importStart:0.4f} seconds."
)
