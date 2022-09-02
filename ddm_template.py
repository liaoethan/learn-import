from configuration import config
from decorators import timer
import json
import logging
import logging.config
import mimetypes
import os
import oauth_token
import requests
import sys
import urllib


@timer
@oauth_token.api_call(200)
def fetch_classname(className):
    logger = logging.getLogger(__name__)
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/classname/fetch-class-name"

    logger.debug(f"Using uri {uri}")
    method = "GET"

    res = session.request(method, uri, headers=headers, params={"value": className})
    logger.debug(f"Response: {res.content}")
    return res


@timer
@oauth_token.api_call(200)
def fetch_template(template_key):
    logger = logging.getLogger(__name__)
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/ddm.ddmtemplate/fetch-template"

    ddm_structure_classname = fetch_classname(
        "com.liferay.dynamic.data.mapping.model.DDMStructure"
    ).json()

    logger.debug(f"Using uri {uri}")
    method = "GET"
    params = {
        "groupId": int(config["SITE_ID"]),
        "classNameId": int(ddm_structure_classname["classNameId"]),
        "templateKey": template_key,
    }

    res = session.request(method, uri, headers=headers, params=params)

    return res


@timer
@oauth_token.api_call(200)
def add_ddm_template(data_definition_id, name, template_key, script, cacheable):
    logger = logging.getLogger(__name__)
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/ddm.ddmtemplate"

    journal_article_classname = fetch_classname(
        "com.liferay.journal.model.JournalArticle"
    ).json()

    ddm_structure_classname = fetch_classname(
        "com.liferay.dynamic.data.mapping.model.DDMStructure"
    ).json()

    logger.debug(f"Using uri {uri}")
    method = "POST"

    data = {
        "method": "add-template",
        "params": {
            "groupId": int(config["SITE_ID"]),
            "classNameId": int(ddm_structure_classname["classNameId"]),
            "classPK": int(data_definition_id),
            "resourceClassNameId": int(journal_article_classname["classNameId"]),
            "templateKey": template_key,
            "nameMap": json.dumps({"en-US": name}),
            "descriptionMap": json.dumps({"en-US": name}),
            "type": "display",
            "mode": "",
            "language": "ftl",
            "script": script,
            "cacheable": cacheable,
            "smallImage": False,
            "smallImageURL": "",
            "smallImageFile": "",
        },
        "id": 123,
        "jsonrpc": "2.0",
    }

    logger.info(f"Executing {json.dumps(data, indent=4)}")
    res = session.request(method, uri, headers=headers, data=json.dumps(data))

    response_payload = res.json()
    if "error" in response_payload:
        raise Exception(
            "Error invoking add-template: " + response_payload["error"]["message"]
        )

    logger.debug(f"Response: {json.dumps(res.json(), indent=4)}")
    return res


@timer
@oauth_token.api_call(200)
def update_ddm_template(data_definition_id, name, template_id, script, cacheable):
    logger = logging.getLogger(__name__)
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/ddm.ddmtemplate"

    logger.debug(f"Using uri {uri}")
    method = "POST"

    data = {
        "method": "update-template",
        "params": {
            "templateId": int(template_id),
            "classPK": int(data_definition_id),
            "nameMap": json.dumps({"en-US": name}),
            "descriptionMap": json.dumps({"en-US": name}),
            "type": "display",
            "mode": "",
            "language": "ftl",
            "script": script,
            "cacheable": cacheable,
        },
        "id": 123,
        "jsonrpc": "2.0",
    }

    res = session.request(method, uri, headers=headers, data=json.dumps(data))

    response_payload = res.json()
    if "error" in response_payload:
        raise Exception(
            "Error invoking update-template: " + response_payload["error"]["message"]
        )
    logger.debug(f"Response: {res.json()}")
    return res
