from configuration import config
from liferay_api.structured_content_folder_rest import (
    post_structured_content_folder,
    get_structured_content_folder_batch,
)
import get_all_items
import logging
import util


def add_missing_structured_content_folders(
    sphinx_article_paths, liferay_structured_content_folders_by_path
):
    """Check all paths in sphinx_article_paths to see if they exist on the server (stored in liferay_structured_content_folders_by_path) and create any missing folders."""
    _logger = logging.getLogger(__name__)
    for sphinx_article_path in sphinx_article_paths:
        if sphinx_article_path not in liferay_structured_content_folders_by_path:
            _logger.info(f"Adding folders for {sphinx_article_path}")
            add_missing_structured_content_folders_for_sphinx_article_path(
                liferay_structured_content_folders_by_path, sphinx_article_path
            )


def add_missing_structured_content_folders_for_sphinx_article_path(
    liferay_structured_content_folders_by_path, sphinx_article_path
):
    """Check all the component path parts for a single path (sphinx_article_path) and add any missing folders"""
    _logger = logging.getLogger(__name__)
    sphinx_article_path_components = sphinx_article_path.split("/")

    parentStructuredContentFolderId = 0

    article_path_prefix = ""
    for sphinx_article_path_component in sphinx_article_path_components:
        article_path = article_path_prefix + sphinx_article_path_component

        _logger.debug(f"Checking article path {article_path}")

        if article_path not in liferay_structured_content_folders_by_path:
            new_liferay_structured_content_folder = post_structured_content_folder(
                sphinx_article_path_component, parentStructuredContentFolderId
            ).json()

            liferay_structured_content_folders_by_path[article_path] = {
                "id": new_liferay_structured_content_folder["id"],
                "parentStructuredContentFolderId": parentStructuredContentFolderId,
            }

            parentStructuredContentFolderId = new_liferay_structured_content_folder[
                "id"
            ]
        else:
            parentStructuredContentFolderId = (
                liferay_structured_content_folders_by_path[article_path]["id"]
            )

        article_path_prefix = article_path + "/"


def get_path(
    liferay_structured_content_folders, liferay_structured_content_folder, path
):
    """Calculate paths for list of structured content folders on the Liferay server"""
    logger = logging.getLogger(__name__)
    logger.debug(
        f"get_path for {liferay_structured_content_folder['name']} and path {path}"
    )

    next_path = (
        liferay_structured_content_folder["name"] + "/" + path
        if path
        else liferay_structured_content_folder["name"]
    )

    if "parentStructuredContentFolderId" in liferay_structured_content_folder:
        return get_path(
            liferay_structured_content_folders,
            next(
                filter(
                    lambda structured_content_folder: structured_content_folder["id"]
                    == liferay_structured_content_folder[
                        "parentStructuredContentFolderId"
                    ],
                    liferay_structured_content_folders,
                )
            ),
            next_path,
        )
    else:
        return next_path


def get_liferay_structured_content_folders_by_path():
    """Prepare a list of structured content folders found on the Liferay server indexed by path"""
    logger = logging.getLogger(__name__)

    liferay_structured_content_folders = get_all_items.get_all_items(
        get_structured_content_folder_batch
    )

    liferay_structured_content_folders_by_path = {}

    for liferay_structured_content_folder in liferay_structured_content_folders:
        liferay_structured_content_folders_by_path[
            get_path(
                liferay_structured_content_folders,
                liferay_structured_content_folder,
                "",
            )
        ] = liferay_structured_content_folder

    util.save_as_json(
        "liferay_structured_content_folders", liferay_structured_content_folders
    )
    util.save_as_json(
        "liferay_structured_content_folders_by_path",
        liferay_structured_content_folders_by_path,
    )
    return liferay_structured_content_folders_by_path
