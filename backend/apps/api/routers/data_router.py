from api.transactions import TransactionRouter

from api import schema
from api.permissions import PermissionChecker
from ontology import export

from typing import List,Union
import logging
logger = logging.getLogger(__name__)

router = TransactionRouter()

@router.get(
    "/search",
    summary = "Searches items that match a certain metadata field",
    description = "Returns all items that based on the search settings match or contain a certain value in a given metadata field",
    response = {200: List[schema.ItemSchema]}
)
@PermissionChecker.has_permission(["DATA_VIEW", "DATA_EXPORT"], require_all=True)
def get_items_through_search(request, tag: str, search: str, case_sensitive: bool, match_full_text: bool):
    logger.info(f"User '{request.user.email}' is searching items that match '{search}' on '{tag}'.")
    
    items = export.search_items(tag, search, not case_sensitive, match_full_text)
    return items

@router.get(
    "/export",
    summary="Gets json or csv from items",
    description="This endpoint gets a csv or json from items",
    response = {200: Union[schema.JSONExportSchema | schema.CSVExportSchema]}
)
@PermissionChecker.has_permission(["DATA_UPLOAD"])
def export_data(request, file_name: str, file_type: str, separator: str, identificator: str, items: str):
  
    data = export.fetch_data_for_export(items, identificator)
    content = export.generate_file_from_data(file_name, file_type, data, separator)
    #logger.debug(f"content = {content}")
    if(file_type=="JSON"):
        return 200, {"data": content}
    if(file_type=="CSV"):
        return 200, {"csv" :content}
    return 200, None