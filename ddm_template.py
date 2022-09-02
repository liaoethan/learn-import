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


@oauth_token.api_call(200)
def fetch_ddm_template(template_key):
    return fetch_template(
        template_key, "com.liferay.dynamic.data.mapping.model.DDMStructure"
    )


@oauth_token.api_call(200)
def fetch_template(template_key, class_name):
    logger = logging.getLogger(__name__)
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": oauth_token.authorization,
        "Content-Type": "application/json",
    }

    classname = fetch_classname(class_name).json()

    uri = f"{config['OAUTH_HOST']}/api/jsonws/ddm.ddmtemplate/fetch-template"

    logger.debug(f"Using uri {uri}")
    method = "GET"
    params = {
        "groupId": int(config["SITE_ID"]),
        "classNameId": int(classname["classNameId"]),
        "templateKey": template_key,
    }

    res = session.request(method, uri, headers=headers, params=params)

    return res


def add_adt_ddm_template(
    class_name,
    data_definition_id,
    name,
    template_key,
    script,
    cacheable,
):
    adt_class_name = fetch_classname(class_name).json()

    portlet_display_template_classname = fetch_classname(
        "com.liferay.portlet.display.template.PortletDisplayTemplate"
    ).json()

    return add_ddm_template(
        adt_class_name["classNameId"],
        portlet_display_template_classname["classNameId"],
        data_definition_id,
        name,
        template_key,
        script,
        cacheable,
    )


def add_journal_article_ddm_template(
    data_definition_id,
    name,
    template_key,
    script,
    cacheable,
):
    journal_article_classname = fetch_classname(
        "com.liferay.journal.model.JournalArticle"
    ).json()

    ddm_structure_classname = fetch_classname(
        "com.liferay.dynamic.data.mapping.model.DDMStructure"
    ).json()

    return add_ddm_template(
        ddm_structure_classname["classNameId"],
        journal_article_classname["classNameId"],
        data_definition_id,
        name,
        template_key,
        script,
        cacheable,
    )


@oauth_token.api_call(200)
def add_ddm_template(
    class_name_id,
    resource_class_name_id,
    data_definition_id,
    name,
    template_key,
    script,
    cacheable,
):
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
        "method": "add-template",
        "params": {
            "groupId": int(config["SITE_ID"]),
            "classNameId": int(class_name_id),
            "classPK": int(data_definition_id),
            "resourceClassNameId": int(resource_class_name_id),
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

    logger.debug(f"Executing {json.dumps(data, indent=4)}")
    res = session.request(method, uri, headers=headers, data=json.dumps(data))

    response_payload = res.json()
    if "error" in response_payload:
        raise Exception(
            "Error invoking add-template: " + response_payload["error"]["message"]
        )

    logger.debug(f"Response: {json.dumps(res.json(), indent=4)}")
    return res


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
