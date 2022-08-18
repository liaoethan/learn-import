import json
import logging
import os
from os.path import exists


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
