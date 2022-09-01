from configuration import config
from get_all_items import get_all_items
from liferay_api.structured_content_rest import get_site_structured_contents_page
import json
import logging
import oauth_token
import requests
import util
from jsonpath_ng.ext import parse


def get_liferay_site_structured_contents_by_friendlyurlpath(article_structure_id):
    sha_256sum_jsonpath = parse(
        '$.contentFields[?(@.label=="sha_256sum")].contentFieldValue.data'
    )
    liferay_site_structured_contents = get_all_items(get_site_structured_contents_page)
    util.save_as_json(
        "liferay_site_structured_contents", liferay_site_structured_contents
    )

    # Only consider articles that are of the Learn Sync structure
    liferay_site_learn_structured_contents = filter(
        lambda site_structured_content: site_structured_content["contentStructureId"]
        == article_structure_id,
        liferay_site_structured_contents,
    )

    liferay_site_structured_contents_by_friendlyurlpath = {}
    for liferay_site_structured_content in liferay_site_learn_structured_contents:
        sha_256sum_jsonpath_find_result = sha_256sum_jsonpath.find(
            liferay_site_structured_content
        )
        sha_256sum = (
            sha_256sum_jsonpath_find_result[0].value
            if len(sha_256sum_jsonpath_find_result) == 1
            else ""
        )

        liferay_site_structured_contents_by_friendlyurlpath[
            liferay_site_structured_content["friendlyUrlPath"]
        ] = {
            "id": liferay_site_structured_content["id"],
            "articleId": liferay_site_structured_content["key"],
            "sha_256sum": sha_256sum,
        }

    util.save_as_json(
        "liferay_site_structured_contents_by_friendlyurlpath",
        liferay_site_structured_contents_by_friendlyurlpath,
    )
    return liferay_site_structured_contents_by_friendlyurlpath
