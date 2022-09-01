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

    uri = f"{config['OAUTH_HOST']}/api/jsonws/invoke"

    logger.debug(f"Using uri {uri}")
    method = "GET"
    cmd = {"/classname/fetch-class-name": {"value": className}}

    logger.debug(f"Executing {json.dumps(cmd, indent=4)}")
    res = session.request(method, uri, headers=headers, data=json.dumps(cmd))
    logger.debug(f"Response: {json.dumps(res.json(), indent=4)}")
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

    uri = f"{config['OAUTH_HOST']}/api/jsonws/invoke"

    ddm_structure_classname = fetch_classname(
        "com.liferay.dynamic.data.mapping.model.DDMStructure"
    ).json()

    logger.debug(f"Using uri {uri}")
    method = "GET"
    cmd = {
        "/ddm.ddmtemplate/fetch-template": {
            "groupId": int(config["SITE_ID"]),
            "classNameId": int(ddm_structure_classname["classNameId"]),
            "templateKey": template_key,
        }
    }

    logger.debug(f"Executing {json.dumps(cmd, indent=4)}")
    res = session.request(method, uri, headers=headers, data=json.dumps(cmd))
    logger.debug(f"Response: {json.dumps(res.json(), indent=4)}")
    return res


@timer
@oauth_token.api_call(200)
def add_ddm_template(data_definition_id, name, template_key, script):
    logger = logging.getLogger(__name__)
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/invoke"

    journal_article_classname = fetch_classname(
        "com.liferay.journal.model.JournalArticle"
    ).json()

    ddm_structure_classname = fetch_classname(
        "com.liferay.dynamic.data.mapping.model.DDMStructure"
    ).json()

    logger.debug(f"Using uri {uri}")
    method = "GET"

    cmd = {
        "/ddm.ddmtemplate/add-template": {
            "groupId": int(config["SITE_ID"]),
            "classNameId": int(ddm_structure_classname["classNameId"]),
            "classPK": int(data_definition_id),
            "resourceClassNameId": int(journal_article_classname["classNameId"]),
            "templateKey": template_key,
            "nameMap": {"en-US": name},
            "descriptionMap": {"en-US": name},
            "type": "display",
            "mode": "",
            "language": "ftl",
            "script": script,
            "cacheable": True,
            "smallImage": False,
            "smallImageURL": "",
            "smallImageFile": "",
        }
    }

    logger.debug(f"Executing {json.dumps(cmd, indent=4)}")
    res = session.request(method, uri, headers=headers, data=json.dumps(cmd))
    logger.debug(f"Response: {json.dumps(res.json(), indent=4)}")
    return res


@timer
@oauth_token.api_call(200)
def update_ddm_template(data_definition_id, name, template_id, script):
    logger = logging.getLogger(__name__)
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    uri = f"{config['OAUTH_HOST']}/api/jsonws/invoke"

    journal_article_classname = fetch_classname(
        "com.liferay.journal.model.JournalArticle"
    ).json()

    ddm_structure_classname = fetch_classname(
        "com.liferay.dynamic.data.mapping.model.DDMStructure"
    ).json()

    logger.debug(f"Using uri {uri}")
    method = "GET"

    cmd = {
        "/ddm.ddmtemplate/update-template": {
            "templateId": int(template_id),
            "classPK": int(data_definition_id),
            "nameMap": {"en-US": name},
            "descriptionMap": {"en-US": name},
            "type": "display",
            "mode": "",
            "language": "ftl",
            "script": script,
            "cacheable": True,
        }
    }

    logger.debug(f"Executing {json.dumps(cmd, indent=4)}")
    res = session.request(method, uri, headers=headers, data=json.dumps(cmd))
    logger.debug(f"Response: {json.dumps(res.json(), indent=4)}")
    return res
