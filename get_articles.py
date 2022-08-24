from configuration import config
import get_all_items
import json
import logging
import oauth_token
import requests
import util
from jsonpath_ng.ext import parse


def get_articles():
    sha_256sum_jsonpath = parse(
        '$.contentFields[?(@.label=="sha_256sum")].contentFieldValue.data'
    )
    articles = get_all_items.get_all_items(get_article_batch)

    articles_by_friendlyurlpath = {}
    for article in articles:
        sha_256sum_jsonpath_find_result = sha_256sum_jsonpath.find(article)
        sha_256sum = (
            sha_256sum_jsonpath_find_result[0].value
            if len(sha_256sum_jsonpath_find_result) == 1
            else ""
        )

        articles_by_friendlyurlpath[article["friendlyUrlPath"]] = {
            "id": article["id"],
            "articleId": article["key"],
            "sha_256sum": sha_256sum,
        }

    util.save_as_json("articles_by_friendlyurlpath", articles_by_friendlyurlpath)
    return articles_by_friendlyurlpath


@oauth_token.api_call(200)
def get_article_batch(page):
    logger = logging.getLogger(__name__)
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    get_uri = f"{config['OAUTH_HOST']}/o/headless-delivery/v1.0/sites/{config['SITE_ID']}/structured-contents?fields=key,contentFields,id,friendlyUrlPath&page={page}&pageSize={config['API_PAGESIZE']}"

    logger.info(f"Fetching article page {page}")
    return requests.get(get_uri, headers=headers)
