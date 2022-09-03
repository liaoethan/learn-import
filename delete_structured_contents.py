from get_all_items import get_all_items
from liferay_api.structured_content_rest import (
    get_site_structured_contents_page,
    delete_structured_content,
)

liferay_site_structured_contents = get_all_items(get_site_structured_contents_page)

for liferay_site_structured_content in liferay_site_structured_contents:
    delete_structured_content(liferay_site_structured_content["id"])
