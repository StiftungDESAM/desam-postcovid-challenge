from api.transactions import TransactionRouter

from django.conf import settings
from neomodel import db
from ninja.errors import HttpError

from api import schema
from api.permissions import PermissionChecker
from ontology import data_requests, diff, export
from ontology.models import OntologyNode
from reviewer.management import create_review_process

from typing import List, Union
import logging
logger = logging.getLogger(__name__)

router = TransactionRouter()

@router.post(
    "/diff",
    summary = "Calculate ontology diff",
    description = "Returns the diff between an uploaded ontology and the current ontology in the database as an RDF-file.",
    response = {200: schema.RDFSchema}
)
@PermissionChecker.has_permission(["ONTOLOGY_VIEW"])
def post_diff(request, body: schema.RDFSchema):
    return 200, {"rdf": diff.from_rdf(body.rdf)}

@router.get(
    "/meta",
    summary = "Queries meta data",
    description = "Queries all available meta data nodes as defined by the query_type",
    response = {200: Union[List[schema.OntologyNodeSchema], schema.RDFSchema]}
)
@PermissionChecker.has_permission(["ONTOLOGY_UPLOAD", "DATA_EXPORT"], require_all=False)
def get_meta_data(request, query_type: str):
    logger.info(f"Query of meta data as {query_type}")
    
    nodes = export.get_metadata_nodes()

    if query_type == "json":
        return 200, nodes
    elif query_type == "rdf":
        # In the RDF, the Metadata and Item nodes are added to conenct all metadata nodes for a prettier look.
        metadata: OntologyNode = OntologyNode.nodes.get(tag = "Metadaten")
        item: OntologyNode = OntologyNode.nodes.get(tag = "Item")
        all_nodes = [metadata, item] + list(nodes)
        entities = data_requests.get_ontology_triplets(nodes = all_nodes)
        rdf = diff.entities_to_rdf(entities)
        return 200, {"rdf": rdf}
    else:
        raise HttpError(400, "Unsupported query type")
    


@router.post(
    "/",
    summary = "Post Ontology Change",
    description = "Returns 201 if successfull 400 if bad request, parses RDF-Diff file from difference and create new review.",
    response = {201: None}
)
@PermissionChecker.has_permission(["ONTOLOGY_UPLOAD"])
def post_ontology(request,body: schema.RDFSchema):
    diff_rdf = diff.from_rdf(body.rdf)
    create_review_process(request.user,diff_rdf)
    return 201, None
    

@router.get(
    "/test",
    summary = "Get all ontology nodes",
    description = "Returns all ontology class nodes currently in the database",
    response = {200: list[schema.SimpleOntologyNodeSchema]}
)
def get_nodes(request):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    nodes = data_requests.get_all_nodes()
    return 200, nodes

@router.post(
    "/test",
    summary = "Create ontology nodes",
    description = "This endpoint creates the given number of ontology nodes. The lowest supported number is 5.",
    response = {200: list[schema.SimpleOntologyNodeSchema]}
)
def post_nodes(request):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    # created_nodes = data_requests.create_nodes(request, nodes.count)
    created_nodes = data_requests.create_example_ontology()
    return 200, created_nodes

@router.delete(
    "/test-DELETE-ALL-ONTOLOGY-NODES",  
    summary = "Delete all ontology nodes",
    description = "This endpoint deletes all ontology nodes in the database",
    response = {204: None},
    auth = None if settings.DEBUG else True
)
def delete_nodes(request):
    # if not settings.DEBUG:
    #     raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    data_requests.delete_all_nodes(request)
    return 204, None


@router.get(
    "/",
    summary = "Returns RDF of ontology",
    description="Returns RDF-Version of actual ontology version in the database",
    response = {200: schema.RDFSchema}
)
@PermissionChecker.has_permission(["ONTOLOGY_VIEW"])
def get_ontology(request):
    #TODO: ist ontology view das richtige hier als Permission?
    entities = data_requests.get_ontology_triplets(request)
    #list = data_requests.resolve_ontology_triplets_into_RDF(triplets)
    #rdf = diff.entities_to_rdf(list)
    rdf =diff.ontology_export_rdf(entities)

    return 200, {"rdf": rdf}

@router.post(
    "/primitive_test_ontology",
    summary = "Create primitive set of ontology nodes",
    description = "This endpoint creates the given number of ontology nodes. The lowest supported number is 5.",
    response = {200: list[schema.SimpleOntologyNodeSchema]}
)
def post_nodes_prim(request, nodes: schema.NodeCount):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    if nodes.count < 5:
        raise HttpError(400, "The number of nodes created must be 5 or greater.")

    created_nodes = data_requests.create_nodes(request, nodes.count)
    return 200, created_nodes


@router.post(
    "/test-baseline-ontology",
    summary = "Create ontology nodes",
    description = "This endpoint creates the given number of ontology nodes. The lowest supported number is 5.",
    response = {200: list[schema.SimpleOntologyNodeSchema]},
    auth = None if settings.DEBUG else True
)
def post_baseline_nodes(request):
    # if not settings.DEBUG:
    #     raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    # created_nodes = data_requests.create_nodes(request, nodes.count)
    created_nodes = data_requests.create_baseline_ontology()
    return 200, created_nodes

