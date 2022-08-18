import get_all_items
import json
import logging
import requests


def get_articles(config, authorization):
    return get_all_items.get_all_items(config, authorization, get_article_batch)


def get_article_batch(page, config, authorization):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": authorization,
        "Content-Type": "application/json",
    }

    session = requests.Session()

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents?fields=id,friendlyUrlPath&page={page}&pageSize={config['API_PAGESIZE']}"

    res = session.get(get_uri, headers=headers)
    logger.debug(f"Fetching article page {page}")
    res = session.get(get_uri, headers=headers)

    if res.status_code != 200:
        errorMessage = "Getting articles failed " + json.dumps(res.json(), indent=4)
        logger.error(errorMessage)
        raise Exception(errorMessage)
    return res.json()
