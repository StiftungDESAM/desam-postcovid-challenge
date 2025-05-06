from api.transactions import TransactionRouter

from django.conf import settings
from neomodel import db
from ninja.errors import HttpError

from knowledge import example_data
from knowledge.graph_functions import set_is_verified_for_subgraph
from knowledge.models import DataNode, load_all_knowledge_node_classes
from ontology.models import OntologyNode

from uuid import uuid4
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='mw_logs_knowledge_router.log')

router = TransactionRouter()


@router.post(
    "/test_primitive",
    summary = "Create knowledge nodes for testing",
    response = {204: None}
)
def post_knowledge_primitive(request):
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


@router.post(
    "/test",
    summary = "Create knowledge nodes for testing",
    response = {204: None}
)
def post_knowledge(request):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    
    forschung_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Forschung")
    studie_node: OntologyNode = OntologyNode.nodes.first_or_none(tag= "Studie")
    datenerhebung_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Datenerhebung")
    fragebogen_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Fragebogen")
    item_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Item")
    metadaten_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Metadaten")
    frage_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Frage")
    feldname_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Feldname")
    
    #teilnehmer_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Teilnehmer")
    if not (forschung_node and studie_node and datenerhebung_node and fragebogen_node and 
            item_node and metadaten_node and frage_node and feldname_node):
        raise HttpError(404, f"Ontology nodes not found.")
    
    
    Forschung = forschung_node.node_class
    Studie = studie_node.node_class
    Datenerhebung = datenerhebung_node.node_class
    Fragebogen = fragebogen_node.node_class
    Item = item_node.node_class
    Metadaten = metadaten_node.node_class
    Frage = frage_node.node_class
    Feldname = feldname_node.node_class
    
    
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



@router.post(
    "/test-study-baseline-ontology-codebook-knowledge",
    summary = "Create knowledge nodes for a simple test study",
    response = {201: None},
    auth = None if settings.DEBUG else True
)
def post_knowledge_test_study(request):
    # if not settings.DEBUG:
    #     raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    
    example_data.create_example_knowledge_graph_for_study_codebook(request)
    
    
    return 201, None

@router.delete(
    "/test-DELETE-ALL-KNOWLEDGE-AND-DATA-NODES",
    summary = "Delete all knowledge and data nodes",
    description = "This endpoint deletes all knowledge and data nodes in the database",
    response = {204: None},
    auth = None if settings.DEBUG else True
)
def delete_nodes(request):
    # if not settings.DEBUG:
    #     raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    example_data.delete_all_knowledge_and_data_nodes(request)
    return 204, None


@router.post(
    "/test-graph-interaction-mw/{study_id}", 
    summary = "test graph interaction methods",
    auth=None,
    response = {201: None}
)
def test_graph_interaction(request, study_id: int):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    load_all_knowledge_node_classes()
    
    #item_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Item")
    #metadaten_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Metadaten")
    #feldname_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Feldname")
    
    #studieninformationen_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Studieninformationen")
    #Studieninformationen = studieninformationen_ontology_node.node_class
    '''
    quality_check_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Qualitaetspruefung")
    data_type_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Datentyp")
    
    Quality_check = quality_check_ontology_node.node_class
    Data_type = data_type_ontology_node.node_class
    
    test_rel_name = get_relationship_field_name(quality_check_ontology_node, data_type_ontology_node)
    #logger.info(f"test_rel_name: {test_rel_name}")
    
    codebook_id = 1
    graph_id = -1
    
    fragebogen_ontology_node: OntologyNode = OntologyNode.nodes.get_or_none(tag = "Fragebogen")
    Fragebogen = fragebogen_ontology_node.node_class
    
    current_fragebogen = Fragebogen.nodes.first_or_none(hat_fragebogenid__current_data__value = str(codebook_id), graph_id = graph_id)[0]
    
    logger.info(f"current Fragebogen: {current_fragebogen}")
    '''
    
    
    
    '''
    study_id = -2
    
    studie_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Studie")
    Studie = studie_ontology_node.node_class
    
    current_study = Studie.nodes.first_or_none(hat_studieninformationen__hat_studienid__current_data__value = str(study_id))
    
    #logger.info(f"current Studie node: {current_study}")
    
    test_item = get_item_by_feldname(graph_id = study_id, field_name = "Trustcenter-ID")
    
    #logger.info(f"test item: {test_item}")
    
    current_patient_id = "5"
    graph_id = -1
    
    patient_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Patient")
    Patient = patient_node.node_class
    
    current_patient_in_review = Patient.nodes.first_or_none(hat_patientid__in_review__value = current_patient_id, graph_id = graph_id)[0]
    
    current_participant_in_review = current_patient_in_review.ist_teilnehmer.single()
    logger.info(f"current patient in review.parents: {current_patient_in_review.ist_teilnehmer.single()}")
    
    
    participant_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Teilnehmer")
    Participant = participant_node.node_class
    '''
    
    graph_id = study_id
    
    # filter leaf node
    set_is_verified_for_subgraph(graph_id = graph_id)
    
    
    
    
    
    #set_graph_verification_true(graph_id = graph_id)
    
    
    
    
    #current_participant_in_review = Participant.nodes.first_or_none(hat_patientid__in_review__value = current_patient_id, graph_id = graph_id)
    logger.info(f"#####################################################")
    # current_participant = Participant.nodes.first_or_none(
    #     Q(hat_patientid__current_data__value = current_patient_id) | Q(hat_patientid__in_review__value = current_patient_id), Q(graph_id = graph_id))
    
    #logger.info(f"current participant: {current_participant}")
    
    #Item = item_node.node_class
    #Metadaten = metadaten_node.node_class
    #Feldname = feldname_node.node_class
    
    #metadaten = Metadaten.create({})[0]
    #feldname = Feldname.create({})[0]
    
    #current_relationship = metadaten_node.children.relationship(feldname_node)
    #custom_rel_name = f"{current_relationship.name}_{feldname_node.tag}".lower()
    
    #rel_manager = getattr(metadaten, custom_rel_name)
    
    #rel_manager.connect(feldname)
    
    #logger.debug(f"get_relationship_label(Metadaten): {Metadaten.get_relationship_label()}")
    #logger.debug(f"get_all_outgoing_relationships(metadaten_node): {ontology.utils.get_all_outgoing_relationships(metadaten_node)}")
    #logger.debug(f": {metadaten_node.children.relationship(feldname_node)}")
    #logger.debug(f": {metadaten_node.children.relationship(feldname_node).name}")

    '''
    drks_id_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "DRKSID")
    studien_id_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "StudienID")
    
    #if not (drks_id_ontology_node and studien_id_ontology_node):
    #    raise HttpError(404, f"Ontology nodes not found.")
    
    DRKSID = drks_id_ontology_node.node_class
    StudienID = studien_id_ontology_node.node_class
    
    test_uuid = "c3cd670e8e254286b66f51a11316ac33"
    test_study_id = -1
    
    node_by_uuid = StudienID.nodes.first_or_none(uuid=test_uuid)
    
    try:
        print()
        #x = StudienID.nodes.get_or_none(uuid = test_uuid)
        x = StudienID.nodes.filter(current_data__value = str(test_study_id), tag = "StudienID").all()
    except:
        raise HttpError(404, f"Ontology nodes not found.")
    
    y = StudienID.nodes.first_or_none(current_data__value = str(test_study_id))[0]
    
    node_by_uuid_uuid = node_by_uuid.current_data.get().value 
    
    # x1 = x.current_data.get().value # AttributeError: 'list' object has no attribute 'current_data'
    #x2 = x[0].current_data.get().value # AttributeError: 'list' object has no attribute 'current_data'
    x3 = x[0][0].current_data.get().value
    #studieninformationen_knowledge_node = Studieninformationen.nodes.get_or_none(uuid = test_uuid)
    
    #a = Studieninformationen.nodes.filter(hat_studienid__current_data__value = str(study_id)).all() # 
    
    #x = StudienID.nodes.filter(current_data__value = str(study_id)).all()
    
    logger.debug(f"#####################################################")
    logger.debug(f"#####################################################")
    logger.debug(f"Test traversal filtering filter().all(): {x}")
    logger.debug(f"Test traversal filtering filter().all().[0]: {x[0]}")
    logger.debug(f"Test traversal filtering filter().all().[0][0]: {x[0][0]}")
    
    logger.debug(f"test get node by first_or_none: {y}")
    logger.debug(f"test get node by uuid: {node_by_uuid}")
    #logger.debug(f"test get node by uuid: {x1}")
    #logger.debug(f"test get node by uuid: {x2}")
    logger.debug(f"test get node by uuid: {node_by_uuid.current_data.get().value}")
    logger.debug(f"test get node by uuid: {x3}")
    logger.debug(f"#####################################################")
    logger.debug(f"#####################################################")
    node_test_uuid = str("6040ed4fb3db407ca84c39272d3d1479")
    
    id = study_id
    
    studien_id_ontology_node = OntologyNode.nodes.first_or_none(tag="StudienID")
    
    if not studien_id_ontology_node:
        raise HttpError(404, "Ontology node 'StudienID' not found")

    StudienID = studien_id_ontology_node.node_class
    
    if not StudienID.nodes.first_or_none(current_data__value = str(id)):
        raise HttpError(404, f"Knowledge node 'StudienID' with data node value {id} not found")
    '''
    
    logger.debug(f"#####################################################")
    #logger.debug(f"item with id test get_or_none: id: {node_test_uuid} result: {Item.nodes.get_or_none(tag = "Item")}")
    
    #logger.debug(f"item with id test get_or_none: id: {node_test_uuid} result: {KnowledgeNode.nodes.get_or_none(uuid = node_test_uuid)}")
    
    #logger.debug(f"item with id test first_or_none: id: {node_test_uuid} result: {KnowledgeNode.nodes.first_or_none(uuid = node_test_uuid)}")
    '''
    if KnowledgeNode.nodes.get_or_none(uuid = node_test_uuid):
        logger.debug(f"#####################################################")
        
    '''
    #logger.debug(f"item with id test: {Item.nodes.get_or_none(id = 130)}")
    #logger.debug(f"item with id test: {Item.nodes.get_or_none(id = '130')}")
    #logger.debug(f": {metadaten}")
    
    
    #add_study_data_to_knowledge_graph(study_id = study_id , data = None)
    
    return 201, None