from configuration import config
import get_all_items
import json
import logging
import oauth_token
import requests


def get_articles():
    return get_all_items.get_all_items(get_article_batch)


@oauth_token.api_call(200)
def get_article_batch(page):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents?fields=id,friendlyUrlPath&page={page}&pageSize={config['API_PAGESIZE']}"

    logger.debug(f"Fetching article page {page}")
    return requests.get(get_uri, headers=headers)
