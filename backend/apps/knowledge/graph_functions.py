from ninja.errors import HttpError
from neomodel import db, Q

from api import schema
from graph_migrations.studies import generate_tag_name
from ontology.models import OntologyNode
from knowledge.models import DataNode, KnowledgeNode
from study.models import Study, CodeBook

from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


def build_study_codebook_knowledge_graph(study: Study) -> None:
    """
    Build a knowledge graph for a study and its codebook based on a Study object.
    
    Args:
        study (Study): The realtional Study model for the study.
    
    Returns:
        None
    """
    # NOTE: build parameters dict 
    knowledge_graph_parameters_dict = {"graph_id": study.id,"is_verified": True}
    
    drks_id_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "DRKSID")
    studien_id_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "StudienID")
    
    if not (drks_id_ontology_node and studien_id_ontology_node):
        raise HttpError(404, f"Ontology nodes not found.")
    
    DRKSID = drks_id_ontology_node.node_class
    StudienID = studien_id_ontology_node.node_class
    
    if StudienID.nodes.filter(current_data__value = str(study.id)).all() :
        raise HttpError(404, f"KnowledgeGraph for this study already exists (id: {study.id}).")
    
    if DRKSID.nodes.filter(current_data__value = str(study.drks_id)).all() :
        raise HttpError(404, f"KnowledgeGraph for study with this DRKS-ID ({study.drks_id}) already exists.")
    
    
    forschung_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Forschung")
    studie_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag= "Studie")
    datenerhebung_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Datenerhebung")
    
    if not (forschung_ontology_node and studie_ontology_node and datenerhebung_ontology_node):
        raise HttpError(404, f"Ontology nodes not found.")
    
    Forschung = forschung_ontology_node.node_class
    Studie = studie_ontology_node.node_class
    Datenerhebung = datenerhebung_ontology_node.node_class
        
    
    forschung = Forschung.create({
        **knowledge_graph_parameters_dict,
        "stakeholder_id": str(uuid4()),
    })[0]
    studie = Studie.create(knowledge_graph_parameters_dict)[0]
    datenerhebung = Datenerhebung.create(knowledge_graph_parameters_dict)[0]
    
    # build subgraph for the study information
    studieninformationen = build_study_information_subgraph(study, knowledge_graph_parameters_dict = knowledge_graph_parameters_dict)
    
    forschung.erstellt_studie.connect(studie, knowledge_graph_parameters_dict)
    studie.hat_studieninformationen.connect(studieninformationen, knowledge_graph_parameters_dict)
    studie.hat_datenerhebung.connect(datenerhebung, knowledge_graph_parameters_dict)
    
    
    for codebook in study.codebooks.all():
        # build subgraph for the codebook
        fragebogen = build_study_codebook_fragebogen_subgraph(codebook, knowledge_graph_parameters_dict = knowledge_graph_parameters_dict)
        
        # connect the codebook to the datenerhebung node
        datenerhebung.hat_fragebogen.connect(fragebogen, knowledge_graph_parameters_dict)



# NOTE: creates the Fragebogen subgraph for one codebook of a study
# Returns the Fragebogen node of the codebook subgraph.
def build_study_codebook_fragebogen_subgraph(codebook: CodeBook, knowledge_graph_parameters_dict: dict) -> KnowledgeNode:
    
    # NOTE: Assumption: These are the only nodes related general codebook information. 
    # If the ontology is extended and new parameters are added to the CodeBook model they need to be added here.
    
    fragebogen_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Fragebogen")
    fragebogen_name_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Fragebogenname")  
    fragebogen_id_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "FragebogenID")  
    

    if not (fragebogen_ontology_node and fragebogen_name_ontology_node and fragebogen_id_ontology_node):
        raise HttpError(404, f"Ontology nodes not found.")
    
    # get the node classes for the fragebogen, fragebogenname and fragebogenid
    Fragebogen = fragebogen_ontology_node.node_class
    Fragebogenname = fragebogen_name_ontology_node.node_class
    FragebogenID = fragebogen_id_ontology_node.node_class
    
    # create the Knowledge nodes for the fragebogen, fragebogenname and fragebogenid
    fragebogen = Fragebogen.create(knowledge_graph_parameters_dict)[0]
    fragebogenname = Fragebogenname.create(knowledge_graph_parameters_dict)[0]
    fragebogen_id = FragebogenID.create(knowledge_graph_parameters_dict)[0]
    
    # create the DataNodes for the fragebogen information
    data_node_fragebogenname = DataNode.create({**knowledge_graph_parameters_dict, "value": codebook.name})[0]
    data_node_fragebogen_id = DataNode.create({**knowledge_graph_parameters_dict, "value": str(codebook.id)})[0]
    
    # connect leaf nodes to connective node (fragebogen)
    fragebogen.hat_fragebogenname.connect(fragebogenname, knowledge_graph_parameters_dict)
    fragebogen.hat_fragebogenid.connect(fragebogen_id, knowledge_graph_parameters_dict)
    
    # connect data nodes to leaf nodes
    fragebogen_id.current_data.connect(data_node_fragebogen_id, knowledge_graph_parameters_dict)
    fragebogenname.current_data.connect(data_node_fragebogenname, knowledge_graph_parameters_dict)
    
    
    # loops over the rows of the codebook and creates item sungraphs for each row and connects them to the fragebogen node
    build_study_codebook_items_subgraphs_and_connect(codebook, fragebogen, knowledge_graph_parameters_dict = knowledge_graph_parameters_dict)
    
    return fragebogen
     
    
def build_study_codebook_items_subgraphs_and_connect(codebook: CodeBook, fragebogen:KnowledgeNode, knowledge_graph_parameters_dict: dict) -> None: 
    
    # get the list of codebook column assigned meta item tags 
    # NOTE: If idx of CodeBookColumn starts at 0/1 for every codebook this step xould be skipped and the respective CodeBookColumn instance could be used directly by idx.
    assigned_meta_tags_list = [
        col.assigned_meta_tag if col.assigned_meta_tag is not None else generate_tag_name(col.header)
        for col in codebook.columns.all()
    ]
    # grab the study.id for the current study
    
    # grab ontology nodes for the item subgraph
    item_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Item")
    spalten_id_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "SpaltenID")
    metadaten_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Metadaten")
    verknuepftes_item_id_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "VerknuepftesItemID")
    
    # 
    Item = item_ontology_node.node_class
    SpaltenID = spalten_id_ontology_node.node_class
    Metadaten = metadaten_ontology_node.node_class
    Verknuepftes_item_id = verknuepftes_item_id_ontology_node.node_class
                
    for row in codebook.rows.all():
        item = Item.create(knowledge_graph_parameters_dict)[0]
        metadaten = Metadaten.create(knowledge_graph_parameters_dict)[0]
        
        fragebogen.hat_item.connect(item, knowledge_graph_parameters_dict)
        item.hat_metadaten.connect(metadaten, knowledge_graph_parameters_dict)
        
        # Add column id for ordering of the items
        spalten_id = SpaltenID.create(knowledge_graph_parameters_dict)[0]
        item.hat_spaltenid.connect(spalten_id, knowledge_graph_parameters_dict)
        spalten_id_data_node = DataNode.create({**knowledge_graph_parameters_dict, "value": str(row.row_id)})[0]
        spalten_id.current_data.connect(spalten_id_data_node, knowledge_graph_parameters_dict)
        
        # Create and connect node for linked item if present in the model
        if row.assigned_item_id:
            
            matched_item = Item.nodes.first_or_none(uuid=row.assigned_item_id)
            if matched_item is None:
                raise HttpError(400, "Invalid linked item")
            
            matched_item_meta = matched_item.hat_metadaten.get_or_none(tag="Metadaten")
            if matched_item_meta is None:
                raise HttpError(400, "Invalid linked item meta")
            
            matched_item_meta_id = matched_item_meta.hat_verknuepftesitemid.get_or_none(tag="VerknuepftesItemID")
            
            id =  row.assigned_item_id
            if matched_item_meta_id is not None:
                id = matched_item_meta_id.current_data.get().value 
                        
            verknuepftes_item_id = Verknuepftes_item_id.create(knowledge_graph_parameters_dict)[0]
            verknuepftes_item_id_data_node = DataNode.create({**knowledge_graph_parameters_dict, "value": str(id)})[0]
            
            metadaten.hat_verknuepftesitemid.connect(verknuepftes_item_id, knowledge_graph_parameters_dict)
            verknuepftes_item_id.current_data.connect(verknuepftes_item_id_data_node, knowledge_graph_parameters_dict)
            
        # enmuerate over the cells for the current row/item and create/attach the respective nodes
        for index, cell in enumerate(row.cells):
                           
            # second part catches newline artifacts
            if cell and not (cell == "\r" or cell == "\n" or cell == "\r\n"):
                
                # search for ontology node with the assigned_meta_tag as tag
                current_leaf_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = assigned_meta_tags_list[index])
                if not current_leaf_ontology_node:
                    raise HttpError(404, f"Ontology node for tag {assigned_meta_tags_list[index]} not found.")
                
                Current_leaf_node = current_leaf_ontology_node.node_class
                current_leaf = Current_leaf_node.create(knowledge_graph_parameters_dict)[0]
                
                # connect the current leaf node to the metadaten node       
                current_relationship = metadaten_ontology_node.children.relationship(current_leaf_ontology_node)
                current_relationship_name = f"{current_relationship.name}_{current_leaf_ontology_node.tag}".lower()
                relationship_manager = getattr(metadaten, current_relationship_name)
                relationship_manager.connect(current_leaf, knowledge_graph_parameters_dict)
                
                # Create and connect DataNode for the current cell value
                current_data_node = DataNode.create({**knowledge_graph_parameters_dict, "value": cell})[0]
                current_leaf.current_data.connect(current_data_node, knowledge_graph_parameters_dict)
                    
    return
    

def build_study_information_subgraph(study: Study, knowledge_graph_parameters_dict: dict) -> KnowledgeNode:
    """
    Build a knowledge graph for the study information subgraph based on a Study object.
    
    Args:
        study (Study): The realtional Study model for the study.
    
    Returns:
        studieninformationen (KnowledgeNode): The central knowledge node for the study information subgraph.
    """
    
    # NOTE: Assumption: These are the only nodes related to study information. 
    # If the ontology is extended and new parameters are added to the study model they need to be added here.
    
    # get the ontology nodes for the study information subgraph
    studieninformationen_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Studieninformationen")
    studienname_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Studienname")
    studienzweck_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Studienzweck")
    beschreibungstext_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Beschreibungstext")
    startdatum_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Startdatum")
    enddatum_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Enddatum")
    drks_id_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "DRKSID")
    studien_id_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "StudienID")
    
    # test if the ontology nodes are found
    if not (studieninformationen_ontology_node and studienname_ontology_node and studienzweck_ontology_node and
            beschreibungstext_ontology_node and startdatum_ontology_node and enddatum_ontology_node and
            drks_id_ontology_node and studien_id_ontology_node):
        raise HttpError(404, f"Ontology nodes not found.")
    
    # get the node classes for the study information subgraph
    Studieninformationen = studieninformationen_ontology_node.node_class
    Studienname = studienname_ontology_node.node_class
    Studienzweck = studienzweck_ontology_node.node_class
    Beschreibungstext = beschreibungstext_ontology_node.node_class
    Startdatum = startdatum_ontology_node.node_class
    Enddatum = enddatum_ontology_node.node_class
    DRKSID = drks_id_ontology_node.node_class
    StudienID = studien_id_ontology_node.node_class
    
    # create the Knowledge nodes for the study information subgraph
    studieninformationen = Studieninformationen.create(knowledge_graph_parameters_dict)[0]
    studienname = Studienname.create(knowledge_graph_parameters_dict)[0]
    studienzweck = Studienzweck.create(knowledge_graph_parameters_dict)[0]
    beschreibungstext = Beschreibungstext.create(knowledge_graph_parameters_dict)[0]
    startdatum = Startdatum.create(knowledge_graph_parameters_dict)[0]
    enddatum = Enddatum.create(knowledge_graph_parameters_dict)[0]
    drks_id = DRKSID.create(knowledge_graph_parameters_dict)[0]
    studien_id = StudienID.create(knowledge_graph_parameters_dict)[0]
    
    # create the DataNodes for the study information
    data_node_studienname = DataNode.create({**knowledge_graph_parameters_dict, "value": study.name})[0]
    data_node_studienzweck = DataNode.create({**knowledge_graph_parameters_dict, "value": study.purpose})[0]
    data_node_beschreibungstext = DataNode.create({**knowledge_graph_parameters_dict, "value": study.description})[0]
    
    # NOTE: Dates have to be converted to string for the DataNode.
    data_node_startdatum = DataNode.create({**knowledge_graph_parameters_dict, "value": str(study.date_start)})[0]
    data_node_enddatum = DataNode.create({**knowledge_graph_parameters_dict, "value": str(study.date_end)})[0]
    
    data_node_drksid = DataNode.create({**knowledge_graph_parameters_dict, "value": study.drks_id})[0]
    data_node_studien_id = DataNode.create({**knowledge_graph_parameters_dict, "value": str(study.id)})[0]
    
    # connect leaf nodes to connective node (studieninformationen)
    studieninformationen.hat_studienname.connect(studienname, knowledge_graph_parameters_dict)
    studieninformationen.hat_studienzweck.connect(studienzweck, knowledge_graph_parameters_dict)
    studieninformationen.hat_beschreibungstext.connect(beschreibungstext, knowledge_graph_parameters_dict)
    studieninformationen.hat_startdatum.connect(startdatum, knowledge_graph_parameters_dict)
    studieninformationen.hat_enddatum.connect(enddatum, knowledge_graph_parameters_dict)
    studieninformationen.hat_drksid.connect(drks_id, knowledge_graph_parameters_dict)
    studieninformationen.hat_studienid.connect(studien_id, knowledge_graph_parameters_dict)
    
    # connect data nodes to leaf nodes
    studienname.current_data.connect(data_node_studienname, knowledge_graph_parameters_dict)
    studienzweck.current_data.connect(data_node_studienzweck, knowledge_graph_parameters_dict)
    beschreibungstext.current_data.connect(data_node_beschreibungstext, knowledge_graph_parameters_dict)
    startdatum.current_data.connect(data_node_startdatum, knowledge_graph_parameters_dict)
    enddatum.current_data.connect(data_node_enddatum, knowledge_graph_parameters_dict)
    drks_id.current_data.connect(data_node_drksid, knowledge_graph_parameters_dict)
    studien_id.current_data.connect(data_node_studien_id, knowledge_graph_parameters_dict)
    
    return studieninformationen





# TODO: functions for data upload into existing (coodebook-)study graph below here

# TODO: add , data: [schema.StudyDataSubmissionSchema] to function signature
def add_study_data_to_knowledge_graph(study_id: int, data: list[schema.StudyDataSubmissionSchema]) -> None:
    # TODO: Check only needed once (in endpoint or here?)
    # check if the study exists in the graph database
    studie_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Studie")
    if not studie_ontology_node:
        raise HttpError(404, "Ontology node 'Studie' not found")
    
    Studie = studie_ontology_node.node_class
    
    current_study_list = Studie.nodes.first_or_none(hat_studieninformationen__hat_studienid__current_data__value = str(study_id))
    
    if not current_study_list:
        raise HttpError(404, f"Knowledge node 'Studien' for study with id {study_id} not found")
    
    current_study = current_study_list[0]
    
    # get graph id of the study 
    graph_id = current_study.graph_id
    data_graph_parameters_dict = {"graph_id": graph_id}

    # TODO: first implementation only adding unverfified data with in_review relationship to DataNodes
    # TODO: later check if there is already present for a specific codebook and if so, update the data
    #for codebook in data
    # loop over the codebooks
    
    
    for codebook_data in data:
        codebook_id = codebook_data.code_book_id
        build_and_attach_quality_check_subgraph(graph_id = graph_id, codebook_id = codebook_id, data_qualitycheck_config = codebook_data.data_quality_check_config)
        # separate the mapping row from the data rows
        mapping_row = codebook_data.values.pop(0)
        #trust_center_id_index = mapping_row.index("TrustCenterID")
        
        # rows are antwortgruppen of patients
        for idx, row in enumerate(codebook_data.values):
            current_patient_id = row[0]
            
            # TODO: check if patient is already present for the current study if not create patient subgraph up to Teilnehmer node
            participant_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Teilnehmer")
            Participant = participant_node.node_class                      
            
            patient_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Patient")
            Patient = patient_node.node_class

            # NOTE: What happens if patient has different IDs for current_data and in_review?
            
            # maybe combine with or in the filtering
            current_patient_current = Patient.nodes.first_or_none(hat_patientid__current_data__value = current_patient_id, graph_id = graph_id)
            current_patient_in_review = Patient.nodes.first_or_none(hat_patientid__in_review__value = current_patient_id, graph_id = graph_id)

            if current_patient_current:
                current_participant = current_patient_current[0].ist_teilnehmer.single()
                
            if current_patient_in_review:
                current_participant = current_patient_in_review[0].ist_teilnehmer.single()
            
            
            # TODO: assumption: all in review data of this study for the current study graph was deleted
            if not (current_patient_current or current_patient_in_review):
                current_participant = add_new_patient_to_study(patient_id = current_patient_id, graph_id = graph_id)        
                current_study.hat_teilnehmer.connect(current_participant, data_graph_parameters_dict)
                
                
                # NOTE: build Antwortgruppen from scratch or update existing one with new values  
                build_or_update_answer_group_from_data(current_participant = current_participant, 
                                                       mapping_row = mapping_row, 
                                                       row_id = idx, 
                                                       data_row = row, 
                                                       graph_id = graph_id, 
                                                       codebook_id = codebook_id
                                                       )
            else: 
                build_or_update_answer_group_from_data(current_participant = current_participant, 
                                                       mapping_row = mapping_row, 
                                                       row_id = idx, 
                                                       data_row = row, 
                                                       graph_id = graph_id, 
                                                       codebook_id = codebook_id
                                                       )

    
    
# TODO: build a new answer group from scratch
# Note the creeation from scatch seems to work
def build_or_update_answer_group_from_data(current_participant: OntologyNode, mapping_row: list[str], row_id: int, data_row: list[str], graph_id: int, codebook_id: int):
    
    data_graph_parameters_dict = {"graph_id": graph_id}
    
    answer_group_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Antwortgruppe")
    AnswerGroup = answer_group_node.node_class
    
    answer_group_id_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "ReihenID")
    AnswerGroupID = answer_group_id_node.node_class
    
    answer_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Antwort")
    Answer = answer_node.node_class
        
    
    #current_answer_group = # NOTE: try to get current answer group based on fragebogen, participant and row id
    answer_group = None
    
    if answer_group:
        # TODO: update existing answer group
        pass
        
        
    else:
        # TODO: build new answer group and answers
        answer_group = AnswerGroup.create({**data_graph_parameters_dict})[0]
        answer_group_id = AnswerGroupID.create({**data_graph_parameters_dict})[0]
        current_fragebogen = get_fragebogen_by_id(graph_id = graph_id, fragebogen_id = codebook_id)
        
        answer_group_id_data_node = DataNode.create({**data_graph_parameters_dict, "value": str(row_id)})[0]
        
        current_participant.gibt_antwortgruppe.connect(answer_group, data_graph_parameters_dict)
        answer_group.hat_reihenid.connect(answer_group_id, data_graph_parameters_dict)
        current_fragebogen.hat_antwortgruppe.connect(answer_group, data_graph_parameters_dict)
        
        answer_group_id.in_review.connect(answer_group_id_data_node, data_graph_parameters_dict)
        
        for index, cell in enumerate(data_row):
            answer = Answer.create({**data_graph_parameters_dict})[0]
            answer_data_node = DataNode.create({**data_graph_parameters_dict, "value": str(cell)})[0]
            current_item = get_item_by_feldname(graph_id = graph_id, field_name = mapping_row[index])
            
            answer_group.hat_antwort.connect(answer, data_graph_parameters_dict)
            current_item.hat_antwort.connect(answer, data_graph_parameters_dict)
            answer.in_review.connect(answer_data_node, data_graph_parameters_dict)
        


# TODO: get the item node of a specific graph by value oif the feldname metadata node
# Note: seems to work
def get_item_by_feldname(graph_id: int, field_name: str) -> OntologyNode:
    
    #feldname_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Feldname")
    item_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Item")
    
    Item = item_ontology_node.node_class
    
    current_item = Item.nodes.first_or_none(hat_metadaten__hat_feldname__current_data__value = str(field_name), graph_id = graph_id)[0]
    
    if not current_item:
        raise HttpError(404, f"Knowledge node 'Item' for field name {field_name} not found")
    
    return current_item


def get_fragebogen_by_id(graph_id: int, fragebogen_id: int) -> KnowledgeNode:
    
    
    fragebogen_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Fragebogen")
    Fragebogen = fragebogen_ontology_node.node_class
    
    current_fragebogen = Fragebogen.nodes.first_or_none(hat_fragebogenid__current_data__value = str(fragebogen_id), graph_id = graph_id)[0]
    
    return current_fragebogen
    



# Add new Patient to a study, return the Teilnehmer node
def add_new_patient_to_study(patient_id: str, graph_id: int) -> OntologyNode:
    
    data_graph_parameters_dict = {"graph_id": graph_id}
    
    patient_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Patient")
    Patient = patient_node.node_class
    
    # maybe combine with or in the filtering
    current_patient_current = Patient.nodes.first_or_none(hat_patientid__current_data__value = patient_id, graph_id = graph_id)
    current_patient_in_review = Patient.nodes.first_or_none(hat_patientid__in_review__value = patient_id, graph_id = graph_id)
    
    if current_patient_current or current_patient_in_review:
        raise HttpError(400, f"Patient with id {patient_id} already exists in the graph database.")
        
    new_patient = Patient.create({**data_graph_parameters_dict, "stakeholder_id": patient_id})[0]
    
    # Create patient ids
    patient_idat_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "PatientIDAT")
    PatientIDAT = patient_idat_node.node_class
    
    patient_id_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "PatientID")
    PatientID = patient_id_node.node_class
    
    new_patient_id = PatientID.create({**data_graph_parameters_dict})[0]
    new_patient_idat = PatientIDAT.create({**data_graph_parameters_dict})[0]
    
    new_patient_id_data = DataNode.create({**data_graph_parameters_dict, "value": patient_id})[0]
    new_patient_idat_data = DataNode.create({**data_graph_parameters_dict, "value": patient_id})[0]
    
    # Connect patient ids
    new_patient.hat_patientid.connect(new_patient_id, data_graph_parameters_dict)
    new_patient.hat_patientidat.connect(new_patient_idat, data_graph_parameters_dict)
    
    new_patient_id.in_review.connect(new_patient_id_data, data_graph_parameters_dict)
    new_patient_idat.in_review.connect(new_patient_idat_data, data_graph_parameters_dict)
    
    participant_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Teilnehmer")
    Participant = participant_node.node_class
    
    # create new participant
    new_participant = Participant.create({**data_graph_parameters_dict})[0]
    
    # connect participant to patient
    new_patient.ist_teilnehmer.connect(new_participant, data_graph_parameters_dict)
    
    return new_participant
    
    








# TODO: extend function to check first if there are already values and then do an update instead of a new creation

# TODO: function that takes graph_id, code_book_id and DataQualityCheckConfig, builds the qualitaetspruefung subgraph and attaches it to the Fragebogen node

def build_and_attach_quality_check_subgraph(
    graph_id: int,
    codebook_id: int,
    data_qualitycheck_config: schema.DataQualityCheckConfig,
    ) -> None:
    
    data_graph_parameters_dict = {"graph_id": graph_id}
    
    quality_check_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Qualitaetspruefung")
    data_type_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Datentyp")
    minimum_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Minimum")
    maximum_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Maximum")
    options_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="Auswahlmoeglichkeiten")
    options_separator_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="TrennzeichenAuswahlmoeglichkeiten")
    answers_separator_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="TrennzeichenAntworten")
    needs_quality_check_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="BenoetigtQualitaetspruefung")
    empty_values_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="LeereWerte")
    empty_rows_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="LeereZeilen")
    empty_columns_ontology_node: OntologyNode = OntologyNode.nodes.first_or_none(tag="LeereSpalten")
    
    if not (quality_check_ontology_node and data_type_ontology_node and minimum_ontology_node and maximum_ontology_node and
            options_ontology_node and options_separator_ontology_node and answers_separator_ontology_node and 
            needs_quality_check_ontology_node and empty_values_ontology_node and empty_rows_ontology_node and
            empty_columns_ontology_node):
        raise HttpError(404, f"Ontology nodes for quality chack subgraph not found")
    
    Quality_check = quality_check_ontology_node.node_class
    Data_type = data_type_ontology_node.node_class
    Minimum = minimum_ontology_node.node_class
    Maximum = maximum_ontology_node.node_class
    Options = options_ontology_node.node_class
    Options_separator = options_separator_ontology_node.node_class
    Answers_separator = answers_separator_ontology_node.node_class
    Needs_quality_check = needs_quality_check_ontology_node.node_class
    Empty_values = empty_values_ontology_node.node_class
    Empty_rows = empty_rows_ontology_node.node_class
    Empty_columns = empty_columns_ontology_node.node_class
    
    logger.info(f"Quality check ontology nodes found")
    
    # create the KnowledgeNodes for the quality check subgraph
    quality_check = Quality_check.create(data_graph_parameters_dict)[0]
    data_type = Data_type.create(data_graph_parameters_dict)[0]
    minimum = Minimum.create(data_graph_parameters_dict)[0]
    maximum = Maximum.create(data_graph_parameters_dict)[0]
    options = Options.create(data_graph_parameters_dict)[0]
    options_separator = Options_separator.create(data_graph_parameters_dict)[0]
    answers_separator = Answers_separator.create(data_graph_parameters_dict)[0]
    needs_quality_check = Needs_quality_check.create(data_graph_parameters_dict)[0]
    empty_values = Empty_values.create(data_graph_parameters_dict)[0]
    empty_rows = Empty_rows.create(data_graph_parameters_dict)[0]
    empty_columns = Empty_columns.create(data_graph_parameters_dict)[0]
    
    # create the DataNodes for the quality check information
    data_type_data_node = DataNode.create({**data_graph_parameters_dict, "value": data_qualitycheck_config.VALUE_TYPE})[0]
    minimum_data_node = DataNode.create({**data_graph_parameters_dict, "value": data_qualitycheck_config.VALUE_RANGE_MIN})[0]
    maximum_data_node = DataNode.create({**data_graph_parameters_dict, "value": data_qualitycheck_config.VALUE_RANGE_MAX})[0]
    options_data_node = DataNode.create({**data_graph_parameters_dict, "value": data_qualitycheck_config.VALUE_MAPPING})[0]
    options_separator_data_node = DataNode.create({**data_graph_parameters_dict, "value": data_qualitycheck_config.mappingSeparator})[0]
    answers_separator_data_node = DataNode.create({**data_graph_parameters_dict, "value": data_qualitycheck_config.answerSeparator})[0]
    needs_quality_check_data_node = DataNode.create({**data_graph_parameters_dict, "value": data_qualitycheck_config.VALUE_REQUIRED})[0]
    empty_values_data_node = DataNode.create({**data_graph_parameters_dict, "value": str(data_qualitycheck_config.EMPTY_VALUES)})[0]
    empty_rows_data_node = DataNode.create({**data_graph_parameters_dict, "value": str(data_qualitycheck_config.EMPTY_ROWS)})[0]
    empty_columns_data_node = DataNode.create({**data_graph_parameters_dict, "value": str(data_qualitycheck_config.EMPTY_COLUMNS)})[0]
    
    # connect leaf nodes to connective node (quality check)    
    quality_check.hat_datentyp.connect(data_type, data_graph_parameters_dict)
    quality_check.hat_minimum.connect(minimum, data_graph_parameters_dict)
    quality_check.hat_maximum.connect(maximum, data_graph_parameters_dict)
    quality_check.hat_auswahlmoeglichkeiten.connect(options, data_graph_parameters_dict)
    quality_check.hat_trennzeichenauswahlmoeglichkeiten.connect(options_separator, data_graph_parameters_dict)
    quality_check.hat_trennzeichenantworten.connect(answers_separator, data_graph_parameters_dict)
    quality_check.hat_benoetigtqualitaetspruefung.connect(needs_quality_check, data_graph_parameters_dict)
    quality_check.hat_leerewerte.connect(empty_values, data_graph_parameters_dict)
    quality_check.hat_leerezeilen.connect(empty_rows, data_graph_parameters_dict)
    quality_check.hat_leerespalten.connect(empty_columns, data_graph_parameters_dict)
    
    # connect data nodes to leaf nodes
    data_type.in_review.connect(data_type_data_node, data_graph_parameters_dict)
    minimum.in_review.connect(minimum_data_node, data_graph_parameters_dict)
    maximum.in_review.connect(maximum_data_node, data_graph_parameters_dict)
    options.in_review.connect(options_data_node, data_graph_parameters_dict)
    options_separator.in_review.connect(options_separator_data_node, data_graph_parameters_dict)
    answers_separator.in_review.connect(answers_separator_data_node, data_graph_parameters_dict)
    needs_quality_check.in_review.connect(needs_quality_check_data_node, data_graph_parameters_dict)
    empty_values.in_review.connect(empty_values_data_node, data_graph_parameters_dict)
    empty_rows.in_review.connect(empty_rows_data_node, data_graph_parameters_dict)
    empty_columns.in_review.connect(empty_columns_data_node, data_graph_parameters_dict)
    
    # connect quality_check to Fragebogen based on the codebook id    
    current_fragebogen = get_fragebogen_by_id(graph_id = graph_id, fragebogen_id = codebook_id)
    current_fragebogen.hat_qualitaetspruefung.connect(quality_check, data_graph_parameters_dict)
    

# TODO: change is_verfied from false to true for all nodes with is_verified = false and graph_id = graph_id

# TODO: only needed for updating the data of an existing study graph
# NOTE: Problem: the easy cypher query will also change the edges for the codebook side of the data graph
def set_current_data_nodes_to_previous_for_subgraph(graph_id: int):
    query = ""
    raise HttpError(501, f"set_current_data_nodes_to_previous not implemented")


def set_in_review_data_to_current_for_subgraph(graph_id: int):
    query = "MATCH (n:LeafNode {graph_id: $graph_id})-[r:IN_REVIEW]->(d:DataNode) CREATE (n)-[:CURRENT]->(d) DELETE r"
    db.cypher_query(query, {"graph_id": graph_id})
    

def set_is_verified_for_subgraph(graph_id: int, is_verified: bool=True):
    # NOTE: set is_verified for all knowledge nodes of a  with graph_id = graph_id
    query = "MATCH (n:KnowledgeNode {graph_id: $graph_id}) SET n.is_verified=$is_verified"
    db.cypher_query(query, {
        "graph_id": graph_id, 
        "is_verified": is_verified})
    
    # NOTE: set is_verified for all edges between KnowedgeNodes of a  with graph_id = graph_id
    #query1 = "MATCH (n:KnowledgeNode {graph_id: $graph_id})-[r]->(m:KnowledgeNode) SET r.is_verified=$is_verified"
    query2 = "MATCH (:KnowledgeNode {graph_id: $graph_id})-[r]->(:KnowledgeNode {graph_id: $graph_id}) SET r.is_verified=$is_verified"
    db.cypher_query(query2, {
        "graph_id": graph_id,         
        "is_verified": is_verified})
    

