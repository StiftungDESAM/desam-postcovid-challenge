from ninja import Router
from ninja.errors import HttpError
from django.conf import settings
from uuid import uuid4
from neomodel import db
from ontology.models import OntologyNode
from knowledge.models import DataNode
from api.permissions import PermissionChecker



router = Router()


@router.post(
    "/test",
    summary = "Create knowledge nodes for testing",
    response = {204: None}
)
@db.transaction
def post_knowledge(request):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    
    patient_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Patient")
    lab_result_node: OntologyNode = OntologyNode.nodes.first_or_none(tag= "LabResult")
    leaf_node_0: OntologyNode = OntologyNode.nodes.first_or_none(tag = "LeafNode0")
    leaf_node_1: OntologyNode = OntologyNode.nodes.first_or_none(tag = "LeafNode1")
    leaf_node_2: OntologyNode = OntologyNode.nodes.first_or_none(tag = "LeafNode2")

    if not (patient_node and lab_result_node and leaf_node_0 and leaf_node_1 and leaf_node_2):
        raise HttpError(404, f"Ontology nodes not found.")

    Patient = patient_node.node_class
    LabResult = lab_result_node.node_class
    LeafNode0 = leaf_node_0.node_class
    LeafNode1 = leaf_node_1.node_class
    LeafNode2 = leaf_node_2.node_class

    patient = Patient.create({
        "stakeholder_id": str(uuid4())
    })[0]
    lab_result = LabResult.create({})[0]
    leaf_0 = LeafNode0.create({})[0]
    leaf_1 = LeafNode1.create({})[0]
    leaf_2 = LeafNode2.create({})[0]

    data_nodes = [{"value": str(i)} for i in range(3)]
    data_nodes = DataNode.create(*data_nodes)

    patient.has_labresult.connect(lab_result)
    lab_result.contains_leafnode0.connect(leaf_0)
    lab_result.contains_leafnode1.connect(leaf_1)
    lab_result.contains_leafnode2.connect(leaf_2)

    leaf_0.current_data.connect(data_nodes[0])
    leaf_1.current_data.connect(data_nodes[1])
    leaf_2.current_data.connect(data_nodes[2])

    return 204, None