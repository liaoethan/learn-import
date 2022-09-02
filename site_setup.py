from functools import cache
import json
from get_all_items import get_all_items
from ddm_template import (
    add_journal_article_ddm_template,
    add_adt_ddm_template,
    fetch_template,
    fetch_ddm_template,
    update_ddm_template,
)
from data_definition_rest import (
    get_site_data_definition_by_content_type_page,
    post_site_data_definition_by_content_type,
    put_data_definition,
)
from document_type import add_file_entry_type_invoke
import logging
from util import save_as_json
import os


def add_adt_templates():
    logger = logging.getLogger(__name__)
    ADT_DIRECTORY = "site-setup/adt/"
    for root, d_names, f_names in os.walk(ADT_DIRECTORY):
        for f in f_names:
            local_file_path = str(os.path.join(root, f))

            _, adt_path = local_file_path.split(ADT_DIRECTORY)

            (
                class_name,
                file_name,
            ) = adt_path.split(os.sep)

            (
                base_file_name,
                extension,
            ) = file_name.split(os.extsep)

            with open(local_file_path) as f:
                template_file_content = f.read()

            cacheable = False

            template_key = base_file_name.upper()
            template_name = base_file_name
            template = fetch_template(template_key, class_name).json()
            if len(template) == 0:
                logger.info(
                    f"Template {template_name} with key {template_key} not found, importing"
                )
                add_adt_ddm_template(
                    class_name,
                    0,
                    template_name,
                    template_key,
                    template_file_content,
                    cacheable,
                )
            else:
                logger.info(f"Template {template_name} found, updating")
                update_ddm_template(
                    0,
                    template_name,
                    template["templateId"],
                    template_file_content,
                    cacheable,
                )


def add_or_update_article_template(
    data_definition_id, template_key, local_file_path, template_name, cacheable
):
    logger = logging.getLogger(__name__)
    template = fetch_ddm_template(template_key).json()

    with open(local_file_path) as f:
        template_file_content = f.read()

    if len(template) == 0:
        logger.info(f"Template {template_name} not found, importing")
        add_journal_article_ddm_template(
            data_definition_id,
            template_name,
            template_key,
            template_file_content,
            cacheable,
        )
    else:
        logger.info(f"Template {template_name} found, updating")
        update_ddm_template(
            data_definition_id,
            template_name,
            template["templateId"],
            template_file_content,
            cacheable,
        )


def check_site_setup():
    logger = logging.getLogger(__name__)

    ARTICLE_CONTENT_TYPE = "journal"
    FILE_ENTRY_CONTENT_TYPE = "document-library"

    article_data_definitions = get_all_items(
        get_site_data_definition_by_content_type_page, ARTICLE_CONTENT_TYPE
    )
    file_entry_data_definitions = get_all_items(
        get_site_data_definition_by_content_type_page, FILE_ENTRY_CONTENT_TYPE
    )

    LEARN_ARTICLE_DATA_DEFINITION_KEY = "LEARN-ARTICLE"
    LEARN_SYNCED_FILE_DATA_DEFINITION_KEY = "LEARN-SYNCED-FILE"

    learn_article_data_definition = next(
        filter(
            lambda article_data_definition: article_data_definition["dataDefinitionKey"]
            == LEARN_ARTICLE_DATA_DEFINITION_KEY,
            article_data_definitions,
        ),
        None,
    )

    learn_synced_file_definition = next(
        filter(
            lambda file_entry_data_definition: file_entry_data_definition[
                "dataDefinitionKey"
            ]
            == LEARN_SYNCED_FILE_DATA_DEFINITION_KEY,
            file_entry_data_definitions,
        ),
        None,
    )

    with open("site-setup/learn_article.json", encoding="utf-8") as f:
        data_definition = json.load(f)

    if learn_article_data_definition is None:
        logger.info("Learn article structure not found, importing")
        learn_article_data_definition = post_site_data_definition_by_content_type(
            ARTICLE_CONTENT_TYPE, data_definition
        ).json()
    else:
        logger.info("Updating Learn article structure")
        learn_article_data_definition = put_data_definition(
            learn_article_data_definition["id"], data_definition
        ).json()

    with open("site-setup/learn_synced_file.json", encoding="utf-8") as f:
        data_definition = json.load(f)

    if learn_synced_file_definition is None:
        logger.info("Learn synced file structure not found, importing")
        learn_synced_file_definition = post_site_data_definition_by_content_type(
            FILE_ENTRY_CONTENT_TYPE, data_definition
        ).json()

        add_file_entry_type_invoke(
            learn_synced_file_definition["id"], "Learn Synced File"
        )
    else:
        logger.info("Updating learn synced file structure")
        learn_synced_file_definition = put_data_definition(
            learn_synced_file_definition["id"], data_definition
        ).json()

    add_or_update_article_template(
        learn_article_data_definition["id"],
        "LEARN-STYLES",
        "styles/main.min.css",
        "Styles",
        False,
    )

    add_or_update_article_template(
        learn_article_data_definition["id"],
        "SVG",
        "styles/svg.html",
        "SVG Sprite",
        False,
    )

    add_or_update_article_template(
        learn_article_data_definition["id"],
        "LEARN-ARTICLE",
        "site-setup/learn_article.ftl",
        "Learn Article Template",
        True,
    )

    add_or_update_article_template(
        learn_article_data_definition["id"],
        "PAGE-ALERT-JS",
        "site-setup/page-alert.js",
        "Page Alert JS",
        False,
    )

    add_adt_templates()
    return (learn_article_data_definition, learn_synced_file_definition)


if __name__ == "__main__":
    check_site_setup()
