import json
import logging
import logging.config
from os.path import exists

logging.config.fileConfig("logging.conf")


def get_config():
    logger = logging.getLogger(__name__)
    configfile = "./config.json"
    localconfigfile = "./config.local.json"

    if exists(localconfigfile):
        configfile = localconfigfile

    logger.info("Using config file" + configfile)

    with open(configfile, encoding="utf-8") as configfile:
        config = json.load(configfile)

    logger.info(
        "Using host "
        + config["OAUTH_HOST"]
        + " and site "
        + config["SITE_ID"]
        + " and structureId "
        + str(config["ARTICLE_STRUCTURE_ID"])
    )

    if (config["IMAGE_IMPORT_LIMIT"]) > 0:
        logger.warning(f"Only importing {config['IMAGE_IMPORT_LIMIT']} images!")
    if (config["ARTICLE_IMPORT_LIMIT"]) > 0:
        logger.warning(f"Only importing {config['ARTICLE_IMPORT_LIMIT']} articles!")
    if (config["API_PAGE_LIMIT"]) > 0:
        logger.warning(
            f"Only fetching {config['API_PAGE_LIMIT']} pages for api get calls"
        )

    return config


config = get_config()
