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

    return config


config = get_config()
