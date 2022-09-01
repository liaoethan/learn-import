import json
from get_all_items import get_all_items
from ddm_template import add_ddm_template, fetch_template, update_ddm_template
from data_definition_rest import (
    get_site_data_definition_by_content_type_page,
    post_site_data_definition_by_content_type,
    put_data_definition,
)
from document_type import add_file_entry_type_invoke
import logging


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
    LEARN_ARTICLE_TEMPLATE_KEY = "LEARN-ARTICLE"
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
        logger.info("Updating learn synced file structure not found")
        learn_synced_file_definition = put_data_definition(
            learn_synced_file_definition["id"], data_definition
        ).json()

    learn_template = fetch_template(LEARN_ARTICLE_TEMPLATE_KEY).json()

    with open("styles/main.min.css") as f:
        style_file_content = f.read()

    with open("site-setup/learn_article.ftl") as f:
        template_file_content = f.read()

    template_file_content_with_styles = (
        f"<style>{style_file_content}</style>{template_file_content}"
    )

    if len(learn_template) == 0:
        logger.info("Learn template not found, importing")
        add_ddm_template(
            learn_article_data_definition["id"],
            "Learn Article Template",
            LEARN_ARTICLE_TEMPLATE_KEY,
            template_file_content_with_styles,
        )
    else:
        logger.info("Learn template found, updating")
        update_ddm_template(
            learn_article_data_definition["id"],
            "Learn Article Template",
            learn_template["templateId"],
            template_file_content_with_styles,
        )

    return (learn_article_data_definition, learn_synced_file_definition)


if __name__ == "__main__":
    check_site_setup()
