from configuration import config
from decorators import timer
import json
import logging
import logging.config
import oauth_token
import requests

logger = logging.getLogger(__name__)


@timer
@oauth_token.api_call(200)
def add_redirect_invoke(sourceURL, destinationURL):
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/invoke"
    logger.info(f"Using uri {uri}")
    method = "POST"
    cmd = [
        {
            "redirect.redirectentry/add-redirect-entry": {
                "groupId": int(config["SITE_ID"]),
                "destinationURL": destinationURL,
                "expirationDate": "2100-01-01",
                "permanent": True,
                "sourceURL": sourceURL,
            }
        }
    ]

    logger.info(f"Executing {json.dumps(cmd, indent=4)}")
    res = session.request(method, uri, headers=headers, data=json.dumps(cmd))
    logger.info(f"Response: {json.dumps(res.json(), indent=4)}")
    print(res.status_code)


@timer
@oauth_token.api_call(200)
def fetch_redirect(redirectEntryId):
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = (
        f"{config['OAUTH_HOST']}/api/jsonws/redirect.redirectentry/get-redirect-entries"
    )
    logger.info(f"Using uri {uri}")
    method = "GET"
    res = session.request(
        method,
        uri,
        headers=headers,
        data=json.dumps(
            {
                "groupId": int(config["SITE_ID"]),
                "start": -1,
                "end": -1,
                "orderByComparator": "",
            }
        ),
    )
    logger.info(f"Response: {res}")
    print(res.status_code)


@timer
@oauth_token.api_call(200)
def add_redirect(sourceURL, destinationURL):
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/redirect.redirectentry/add-redirect-entry"
    logger.info(f"Using uri {uri}")
    method = "GET"
    params = {
        "groupId": int(config["SITE_ID"]),
        "destinationURL": destinationURL,
        "expirationDate": "2100-01-01",
        # "expirationDate": 0,
        "permanent": True,
        "sourceURL": sourceURL,
    }

    logger.info(f"Executing {json.dumps(params, indent=4)}")
    res = session.request(method, uri, headers=headers, params=params)
    logger.info(f"Response: {res.content}")
    print(res.status_code)


add_redirect(
    "commerce/latest/ja/developer-guide/content/adding-a-new-product-data-source-for-the-product-publisher-widget.html",
    "https://learn-uat.lxc.liferay.com/ja/web/learn/w/commerce/developer-guide/content/adding-a-new-product-data-source-for-the-product-publisher-widget.html",
)

# fetch_redirect(718290)
