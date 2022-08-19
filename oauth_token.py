from configuration import config
import json
import logging
import requests


def get_oauth_token():
    logger = logging.getLogger(__name__)

    post_uri = config["OAUTH_HOST"] + "/o/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    session = requests.Session()
    res = session.post(
        post_uri,
        headers=headers,
        data={
            "client_id": config["CLIENT_ID"],
            "client_secret": config["CLIENT_SECRET"],
            "grant_type": "client_credentials",
        },
    )

    if not res.status_code == 200:
        error_message = f"Failed to get oauth token {json.dumps(res.json(), indent=4)}"
        logger.error(error_message)
        raise Exception(error_message)

    logger.info("Received OAuth token")
    token_payload = res.json()
    authorization = f"{token_payload['token_type']} {token_payload['access_token']}"

    return authorization
