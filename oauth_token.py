from configuration import config
from decorators import timer
import functools
import json
import logging
import requests


class AuthClientError(Exception):
    """Base class for other exceptions"""

    pass


@timer
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


authorization = get_oauth_token()


def renew_access_token(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global authorization
        try:
            return func(*args, **kwargs)
        except AuthClientError:
            logger = logging.getLogger(func.__name__)
            logger.warning("Token possibly expired, trying again")
            authorization = get_oauth_token()
            return func(*args, **kwargs)

    return wrapper


def api_call(success_code=200):
    def decorate(func):
        @renew_access_token
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if res is None:
                return
            if not res.status_code == success_code:
                logger = logging.getLogger(func.__name__)
                try:
                    error_message = f"API call for {func.__name__} failed with return code: {res.status_code} and error message {json.dumps(res.json(), indent=4)}"
                except json.JSONDecodeError:
                    error_message = f"API call for {func.__name__} failed with return code: {res.status_code} and error message {res}"
                logger.error(error_message)
                if res.status_code == 401 or res.status_code == 403:
                    raise AuthClientError
                else:
                    raise Exception(error_message)
            return res

        return wrapper

    return decorate
