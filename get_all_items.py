import logging
import time


def getAllItems(config, authorization, callback):
    logger = logging.getLogger(__name__)

    getStart = time.perf_counter()

    items = []
    page = 1
    fetchedAllItems = False

    while not fetchedAllItems:
        itemBatch = callback(page, config, authorization)
        items += itemBatch["items"]
        if itemBatch["lastPage"] == page:
            fetchedAllItems = True
        page = page + 1

    getEnd = time.perf_counter()

    logger.info(f"Fetched {len(items)} items in {getEnd - getStart:0.4f} seconds.")
    return items
