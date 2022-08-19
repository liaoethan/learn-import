from configuration import config
import logging
import time


def get_all_items(authorization, callback):
    logger = logging.getLogger(__name__)

    get_start = time.perf_counter()

    items = []
    page = 1
    fetched_all_items = False

    while not fetched_all_items:
        item_batch = callback(page, authorization)
        items += item_batch["items"]
        if item_batch["lastPage"] == page:
            fetched_all_items = True
        page = page + 1

    get_end = time.perf_counter()

    logger.info(f"Fetched {len(items)} items in {get_end - get_start:0.4f} seconds.")
    return items
