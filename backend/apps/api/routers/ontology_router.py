from ninja import Router
from ninja.errors import HttpError
from django.conf import settings

from neomodel import db
from api import schema

from ontology import data_requests
from api.permissions import PermissionChecker


router = Router()



@router.get(
    "/test",
    summary = "Get all ontology nodes",
    description = "Returns all ontology class nodes currently in the database",
    response = {200: list[schema.OntologyNodeSchema]}
)
def get_nodes(request):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    nodes = data_requests.get_all_nodes(request)
    return 200, nodes

@router.post(
    "/test",
    summary = "Create ontology nodes",
    description = "This endpoint creates the given number of ontology nodes. The lowest supported number is 5.",
    response = {200: list[schema.OntologyNodeSchema]}
)
@db.transaction
def post_nodes(request, nodes: schema.NodeCount):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    if nodes.count < 5:
        raise HttpError(400, "The number of nodes created must be 5 or greater.")

    created_nodes = data_requests.create_nodes(request, nodes.count)
    return 200, created_nodes

@router.delete(
    "/test",
    summary = "Delete all ontology nodes",
    description = "This endpoint deletes all ontology nodes in the database",
    response = {204: None}
)
@db.transaction
def delete_nodes(request):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    data_requests.delete_all_nodes(request)
    return 204, None
