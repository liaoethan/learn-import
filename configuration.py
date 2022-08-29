import json
import logging
import logging.config
from os.path import exists
import argparse

logging.config.fileConfig("logging.conf")


def get_config():
    logger = logging.getLogger(__name__)
    configfile = "./config.json"

    parser = argparse.ArgumentParser(prog="Learn Import")
    parser.add_argument(
        "--config",
        default="./config.local.json",
        help="Configuration file name, i.e. ./config.lxc.json, defaults to ./config.local.json",
        required=False,
    )
    args = parser.parse_args()

    if exists(args.config):
        configfile = args.config

    logger.info("Using config file" + configfile)

    with open(configfile, encoding="utf-8") as configfile:
        config = json.load(configfile)

    logger.info("Using host " + config["OAUTH_HOST"] + " and site " + config["SITE_ID"])

    if (config["DOCUMENT_IMPORT_LIMIT"]) > 0:
        logger.warning(f"Only importing {config['DOCUMENT_IMPORT_LIMIT']} images!")
    if (config["STRUCTURED_CONTENT_IMPORT_LIMIT"]) > 0:
        logger.warning(
            f"Only importing {config['STRUCTURED_CONTENT_IMPORT_LIMIT']} articles!"
        )
    if (config["API_PAGE_LIMIT"]) > 0:
        logger.warning(
            f"Only fetching {config['API_PAGE_LIMIT']} pages for api get calls"
        )

    return config


config = get_config()
