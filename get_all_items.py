from configuration import config
from decorators import timer
import logging


@timer
def get_all_items(callback):
    logger = logging.getLogger(__name__)

    items = []
    page = 1
    fetched_all_items = False

    while not fetched_all_items:
        item_batch = callback(page).json()
        items += item_batch["items"]
        if item_batch["lastPage"] == page:
            fetched_all_items = True
        page = page + 1

    logger.info(f"Fetched {len(items)} items.")
    return items
