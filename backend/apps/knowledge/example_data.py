
from ninja.errors import HttpError
from django.conf import settings
from uuid import uuid4
from neomodel import db
from ontology.models import OntologyNode
from knowledge.models import DataNode
from knowledge.models import load_all_knowledge_node_classes
import logging

logger = logging.getLogger(__name__)


def delete_all_knowledge_and_data_nodes(request) -> None:
    """Delete all knowledge and data graph nodes."""
    
    db.cypher_query("MATCH (n:KnowledgeNode|DataNode) DETACH DELETE n")



def create_example_knowledge_graph_for_study_codebook(request) -> None:
    """Create an example knowledge graph for study codebook."""

    load_all_knowledge_node_classes()
    
    # NOTE: build dict to use for passing parameters in node/relationship creation
    # negative numbers used for hard coded dummy data. -1 for study 1
    study_1_id = 1
    knowledge_graph_parameters_dict_1 = {"graph_id": study_1_id, "is_verified": True}
    
    logger.debug("loading ontology nodes start")
    
    forschung_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Forschung")
    studie_node: OntologyNode = OntologyNode.nodes.first_or_none(tag= "Studie")
    datenerhebung_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Datenerhebung")
    fragebogen_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Fragebogen")
    item_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Item")
    spalten_id_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "SpaltenID")
    metadaten_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Metadaten")
    feldname_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Feldname")
    verknuepftesitemid_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "VerknuepftesItemID")
    
    studieninformationen_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Studieninformationen")
    studienname_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Studienname")
    studienzweck_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Studienzweck")
    beschreibungstext_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Beschreibungstext")
    startdatum_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Startdatum")
    enddatum_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Enddatum")
    drks_id_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "DRKSID")
    studien_id_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "StudienID")
      
    fragebogen_name_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Fragebogenname")  
    fragebogen_id_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "FragebogenID")  
    
    #logger.debug(forschung_node)
    
    
    
    #teilnehmer_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Teilnehmer")
    if not (forschung_node and studie_node and datenerhebung_node and fragebogen_node and item_node and 
            metadaten_node and feldname_node and studieninformationen_node and studienname_node and studienzweck_node and
            beschreibungstext_node and startdatum_node and enddatum_node and drks_id_node and studien_id_node and
            fragebogen_name_node and fragebogen_id_node):
        raise HttpError(404, f"Ontology nodes not found.")
    
    

    Forschung = forschung_node.node_class
    Studie = studie_node.node_class
    Datenerhebung = datenerhebung_node.node_class
    Fragebogen = fragebogen_node.node_class
    Item = item_node.node_class
    SpaltenID = spalten_id_node.node_class
    Metadaten = metadaten_node.node_class
    Feldname = feldname_node.node_class
    LinkedItem = verknuepftesitemid_node.node_class
    
    Studieninformationen = studieninformationen_node.node_class
    Studienname = studienname_node.node_class
    Studienzweck = studienzweck_node.node_class
    Beschreibungstext = beschreibungstext_node.node_class
    Startdatum = startdatum_node.node_class
    Enddatum = enddatum_node.node_class
    DRKSID = drks_id_node.node_class
    StudienID = studien_id_node.node_class
    
    Fragebogenname = fragebogen_name_node.node_class
    FragebogenID = fragebogen_id_node.node_class
    
    
    logger.debug("loaded ontology node classes")
    
    # Study 1
    forschung = Forschung.create({
        **knowledge_graph_parameters_dict_1,
        "stakeholder_id": str(uuid4())
    })[0]
    studie0 = Studie.create(knowledge_graph_parameters_dict_1)[0]
    
    studieninformationen = Studieninformationen.create(knowledge_graph_parameters_dict_1)[0]
    studienname = Studienname.create(knowledge_graph_parameters_dict_1)[0]
    studienzweck = Studienzweck.create(knowledge_graph_parameters_dict_1)[0]
    beschreibungstext = Beschreibungstext.create(knowledge_graph_parameters_dict_1)[0]
    startdatum = Startdatum.create(knowledge_graph_parameters_dict_1)[0]
    enddatum = Enddatum.create(knowledge_graph_parameters_dict_1)[0]
    drks_id = DRKSID.create(knowledge_graph_parameters_dict_1)[0]
    studien_id = StudienID.create(knowledge_graph_parameters_dict_1)[0]
    
    datenerhebung = Datenerhebung.create(knowledge_graph_parameters_dict_1)[0]
    fragebogen0 = Fragebogen.create(knowledge_graph_parameters_dict_1)[0]
    item0 = Item.create(knowledge_graph_parameters_dict_1)[0]
    item1 = Item.create(knowledge_graph_parameters_dict_1)[0]
    spalten_id0 = SpaltenID.create(knowledge_graph_parameters_dict_1)[0]
    spalten_id1 = SpaltenID.create(knowledge_graph_parameters_dict_1)[0]
    metadaten0 = Metadaten.create(knowledge_graph_parameters_dict_1)[0]
    metadaten1 = Metadaten.create(knowledge_graph_parameters_dict_1)[0]
    feldname0 = Feldname.create(knowledge_graph_parameters_dict_1)[0]
    feldname1 = Feldname.create(knowledge_graph_parameters_dict_1)[0]
    
    fragebogenname = Fragebogenname.create(knowledge_graph_parameters_dict_1)[0]
    fragebogen_id = FragebogenID.create(knowledge_graph_parameters_dict_1)[0]
    
    # study info data node creation
    data_node_studienname = DataNode.create({"value": "First test Study"})
    data_node_studienzweck = DataNode.create({"value": "FEASIBILITY_CHECK"})
    data_node_beschreibungstext = DataNode.create({"value": "Simple test study to test knowledge graph creation"})
    data_node_startdatum = DataNode.create({"value": "2025-04-20"})
    data_node_enddatum = DataNode.create({"value": "2025-04-20"})
    data_node_drksid = DataNode.create({"value": "DRKS000Test01"})
    
    
    #NOTE: how do we deal with studien-ID? -> just use id from the realtional study model
    #data_node_studienid = DataNode.create({"value": "1"})
    data_node_studienid = DataNode.create({"value": str(study_1_id)})
    
    
    data_node_spalten_id0 = DataNode.create({"value": "0"})
    data_node_spalten_id1 = DataNode.create({"value": "1"})
    data_node_feldname0 = DataNode.create({"value": "Trustcenter-ID"})
    data_node_feldname1 = DataNode.create({"value": "Alter"})
    
    data_node_fragebogenname = DataNode.create({"value": "Test_codebook_1"})
    
    #NOTE: how do we deal with fragebogen-ID? -> just use id from the realtional codebook model
    data_node_fragebogen_id = DataNode.create({"value": "1"})
    fragebogen_id.current_data.connect(data_node_fragebogen_id[0])
    
    fragebogenname.current_data.connect(data_node_fragebogenname[0])
    
    
    forschung.erstellt_studie.connect(studie0, knowledge_graph_parameters_dict_1)
    studie0.hat_datenerhebung.connect(datenerhebung)
    
    studie0.hat_studieninformationen.connect(studieninformationen, knowledge_graph_parameters_dict_1)
    studieninformationen.hat_studienname.connect(studienname, knowledge_graph_parameters_dict_1)
    studieninformationen.hat_studienzweck.connect(studienzweck, knowledge_graph_parameters_dict_1)
    studieninformationen.hat_beschreibungstext.connect(beschreibungstext, knowledge_graph_parameters_dict_1)
    studieninformationen.hat_startdatum.connect(startdatum, knowledge_graph_parameters_dict_1)
    studieninformationen.hat_enddatum.connect(enddatum, knowledge_graph_parameters_dict_1)
    studieninformationen.hat_drksid.connect(drks_id, knowledge_graph_parameters_dict_1)
    studieninformationen.hat_studienid.connect(studien_id, knowledge_graph_parameters_dict_1)
    
    # study information data node connection
    studienname.current_data.connect(data_node_studienname[0])
    studienzweck.current_data.connect(data_node_studienzweck[0])
    beschreibungstext.current_data.connect(data_node_beschreibungstext[0])
    startdatum.current_data.connect(data_node_startdatum[0])
    enddatum.current_data.connect(data_node_enddatum[0])
    drks_id.current_data.connect(data_node_drksid[0])
    studien_id.current_data.connect(data_node_studienid[0])
    
    
    datenerhebung.hat_fragebogen.connect(fragebogen0, knowledge_graph_parameters_dict_1)
    
    fragebogen0.hat_fragebogenname.connect(fragebogenname, knowledge_graph_parameters_dict_1)
    
    
    fragebogen0.hat_fragebogenid.connect(fragebogen_id, knowledge_graph_parameters_dict_1)
    
    fragebogen0.hat_item.connect(item0, knowledge_graph_parameters_dict_1)        
    item0.hat_metadaten.connect(metadaten0, knowledge_graph_parameters_dict_1)
    item0.hat_spaltenid.connect(spalten_id0, knowledge_graph_parameters_dict_1)
    metadaten0.hat_feldname.connect(feldname0, knowledge_graph_parameters_dict_1)

    spalten_id0.current_data.connect(data_node_spalten_id0[0])
    feldname0.current_data.connect(data_node_feldname0[0])
    
    fragebogen0.hat_item.connect(item1, knowledge_graph_parameters_dict_1)
    item1.hat_metadaten.connect(metadaten1, knowledge_graph_parameters_dict_1)
    item1.hat_spaltenid.connect(spalten_id1, knowledge_graph_parameters_dict_1)
    metadaten1.hat_feldname.connect(feldname1, knowledge_graph_parameters_dict_1)
    
    spalten_id1.current_data.connect(data_node_spalten_id1[0])
    feldname1.current_data.connect(data_node_feldname1[0])
    
    # NOTE: Study 2
    # Study 2
    study_2_id = 2
    # NOTE: build dict to use for passing parameters in node/relationship creation
    # negative numbers used for hard coded dummy data. -2 for study 2
    knowledge_graph_parameters_dict_2 = {"graph_id": study_2_id, "is_verified": False}
    
    forschung = Forschung.create({
        **knowledge_graph_parameters_dict_2,
        "stakeholder_id": str(uuid4())
    })[0]
    studie1 = Studie.create(knowledge_graph_parameters_dict_2)[0]
    
    studieninformationen = Studieninformationen.create(knowledge_graph_parameters_dict_2)[0]
    studienname = Studienname.create(knowledge_graph_parameters_dict_2)[0]
    studienzweck = Studienzweck.create(knowledge_graph_parameters_dict_2)[0]
    beschreibungstext = Beschreibungstext.create(knowledge_graph_parameters_dict_2)[0]
    startdatum = Startdatum.create(knowledge_graph_parameters_dict_2)[0]
    enddatum = Enddatum.create(knowledge_graph_parameters_dict_2)[0]
    drks_id = DRKSID.create(knowledge_graph_parameters_dict_2)[0]
    studien_id = StudienID.create(knowledge_graph_parameters_dict_2)[0]
    
    datenerhebung = Datenerhebung.create(knowledge_graph_parameters_dict_2)[0]
    fragebogen1 = Fragebogen.create(knowledge_graph_parameters_dict_2)[0]
    item2 = Item.create(knowledge_graph_parameters_dict_2)[0]
    item3 = Item.create(knowledge_graph_parameters_dict_2)[0]
    spalten_id2 = SpaltenID.create(knowledge_graph_parameters_dict_2)[0]
    spalten_id3 = SpaltenID.create(knowledge_graph_parameters_dict_2)[0]
    metadaten2 = Metadaten.create(knowledge_graph_parameters_dict_2)[0]
    metadaten3 = Metadaten.create(knowledge_graph_parameters_dict_2)[0]
    feldname0 = Feldname.create(knowledge_graph_parameters_dict_2)[0]
    feldname1 = Feldname.create(knowledge_graph_parameters_dict_2)[0]
    
    fragebogenname = Fragebogenname.create(knowledge_graph_parameters_dict_2)[0]
    fragebogen_id = FragebogenID.create(knowledge_graph_parameters_dict_2)[0]
    
    # study info data node creation
    data_node_studienname = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "Second test Study"})
    data_node_studienzweck = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "FEASIBILITY_CHECK"})
    data_node_beschreibungstext = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "Simple test study to test knowledge graph creation"})
    data_node_startdatum = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "2025-04-20"})
    data_node_enddatum = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "2025-04-20"})
    data_node_drksid = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "DRKS000Test2"})
    
    
    #NOTE: how do we deal with studien-ID? -> just use id from the realtional study model
    data_node_studienid = DataNode.create({**knowledge_graph_parameters_dict_2, "value": str(study_2_id)})
    data_node_feldname0 = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "Trustcenter-ID"})
    data_node_feldname1 = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "Alter"})
    data_node_spalten_id2 = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "0"})
    data_node_spalten_id3 = DataNode.create({**knowledge_graph_parameters_dict_2, "value": "1"})
    
    
    data_node_fragebogenname = DataNode.create({**knowledge_graph_parameters_dict_2,"value": "Test_codebook_1"})
    
    #NOTE: how do we deal with fragebogen-ID? -> just use id from the realtional codebook model
    data_node_fragebogen_id = DataNode.create({**knowledge_graph_parameters_dict_2,"value": "1"})
    fragebogen_id.current_data.connect(data_node_fragebogen_id[0], knowledge_graph_parameters_dict_2)
    
    fragebogenname.current_data.connect(data_node_fragebogenname[0], knowledge_graph_parameters_dict_2)
    
    
    forschung.erstellt_studie.connect(studie1, knowledge_graph_parameters_dict_2)
    studie1.hat_datenerhebung.connect(datenerhebung, knowledge_graph_parameters_dict_2)
    
    studie1.hat_studieninformationen.connect(studieninformationen, knowledge_graph_parameters_dict_2)
    studieninformationen.hat_studienname.connect(studienname, knowledge_graph_parameters_dict_2)
    studieninformationen.hat_studienzweck.connect(studienzweck, knowledge_graph_parameters_dict_2)
    studieninformationen.hat_beschreibungstext.connect(beschreibungstext, knowledge_graph_parameters_dict_2)
    studieninformationen.hat_startdatum.connect(startdatum, knowledge_graph_parameters_dict_2)
    studieninformationen.hat_enddatum.connect(enddatum, knowledge_graph_parameters_dict_2)
    studieninformationen.hat_drksid.connect(drks_id, knowledge_graph_parameters_dict_2)
    studieninformationen.hat_studienid.connect(studien_id, knowledge_graph_parameters_dict_2)
    
    # study information data node connection
    studienname.current_data.connect(data_node_studienname[0], knowledge_graph_parameters_dict_2)
    studienzweck.current_data.connect(data_node_studienzweck[0], knowledge_graph_parameters_dict_2)
    beschreibungstext.current_data.connect(data_node_beschreibungstext[0], knowledge_graph_parameters_dict_2)
    startdatum.current_data.connect(data_node_startdatum[0], knowledge_graph_parameters_dict_2)
    enddatum.current_data.connect(data_node_enddatum[0], knowledge_graph_parameters_dict_2)
    drks_id.current_data.connect(data_node_drksid[0], knowledge_graph_parameters_dict_2)
    studien_id.current_data.connect(data_node_studienid[0], knowledge_graph_parameters_dict_2)
    
    
    datenerhebung.hat_fragebogen.connect(fragebogen1, knowledge_graph_parameters_dict_2)
    fragebogen1.hat_fragebogenname.connect(fragebogenname, knowledge_graph_parameters_dict_2)
    fragebogen1.hat_fragebogenid.connect(fragebogen_id, knowledge_graph_parameters_dict_2)
   
    
    fragebogen1.hat_item.connect(item2, knowledge_graph_parameters_dict_2)        
    item2.hat_metadaten.connect(metadaten2, knowledge_graph_parameters_dict_2)
    item2.hat_spaltenid.connect(spalten_id2, knowledge_graph_parameters_dict_2)
    metadaten2.hat_feldname.connect(feldname0, knowledge_graph_parameters_dict_2)

    spalten_id2.current_data.connect(data_node_spalten_id2[0], knowledge_graph_parameters_dict_2)
    feldname0.current_data.connect(data_node_feldname0[0], knowledge_graph_parameters_dict_2)
    
    
    fragebogen1.hat_item.connect(item3, knowledge_graph_parameters_dict_2)
    item3.hat_metadaten.connect(metadaten3, knowledge_graph_parameters_dict_2)
    item3.hat_spaltenid.connect(spalten_id3, knowledge_graph_parameters_dict_2)
    metadaten3.hat_feldname.connect(feldname1, knowledge_graph_parameters_dict_2)    
    
    spalten_id3.current_data.connect(data_node_spalten_id3[0], knowledge_graph_parameters_dict_2)
    feldname1.current_data.connect(data_node_feldname1[0], knowledge_graph_parameters_dict_2)
    
    
    # Study 1 linked item
    linked_item1 = LinkedItem.create(knowledge_graph_parameters_dict_1)[0]
    data_node_linked_item1 = DataNode.create({**knowledge_graph_parameters_dict_1, "value": item3.uuid})
    metadaten1.hat_verknuepftesitemid.connect(linked_item1, knowledge_graph_parameters_dict_1)
    linked_item1.current_data.connect(data_node_linked_item1[0], knowledge_graph_parameters_dict_1)
    
    
    #logger.debug("###################################################################")
    #logger.debug(data_node_feldname0)
    #logger.debug(data_node_feldname0[0])
    #logger.debug("###################################################################")
    
    
    # NOTE: This is a test for the Leistungserbringer node creation (multiple stakeholder nodes with same id). Uncomment if needed. 
    '''
    leistungserbringer_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Leistungserbringer")
    Leistungserbringer = leistungserbringer_node.node_class
    
    leistungserbringer = Leistungserbringer.create({
        "stakeholder_id": "0001"
    })[0]
    '''
    
    # Add exmaple answer data
    # For every uploaded data row a answer group needs to created that is related to the uploader, questionnaire and its answers
    
    # NOTE: parameterset with is_verified = False for the data upload
    knowledge_graph_parameters_dict_1_unverified = {"graph_id": study_1_id, "is_verified": False}

    SET_DATA_UNVERIFIED = True
    parameter_dict = knowledge_graph_parameters_dict_1_unverified if SET_DATA_UNVERIFIED else knowledge_graph_parameters_dict_1
    #parameter_dict = {"graph_id": study_1_id, "is_verified": False}
    
    # Create patients and participants
    patient_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Patient")
    Patient = patient_node.node_class
    
    patient1 = Patient.create({**parameter_dict, "stakeholder_id": "0001"})[0]
    patient2 = Patient.create({**parameter_dict, "stakeholder_id": "0002"})[0]
    patient3 = Patient.create({**parameter_dict, "stakeholder_id": "0003"})[0]
    patient4 = Patient.create({**parameter_dict, "stakeholder_id": "0004"})[0]
    patient5 = Patient.create({**parameter_dict, "stakeholder_id": "0005"})[0]
    patient6 = Patient.create({**parameter_dict, "stakeholder_id": "0006"})[0]
    patient7 = Patient.create({**parameter_dict, "stakeholder_id": "0007"})[0]
    patient8 = Patient.create({**parameter_dict, "stakeholder_id": "0008"})[0]
    patient9 = Patient.create({**parameter_dict, "stakeholder_id": "0009"})[0]
    patient10 = Patient.create({**parameter_dict, "stakeholder_id": "00010"})[0]
    
    participant_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Teilnehmer")
    Participant = participant_node.node_class
    
    participant1 = Participant.create({**parameter_dict})[0]
    participant2 = Participant.create({**parameter_dict})[0]
    participant3 = Participant.create({**parameter_dict})[0]
    participant4 = Participant.create({**parameter_dict})[0]
    participant5 = Participant.create({**parameter_dict})[0]
    participant6 = Participant.create({**parameter_dict})[0]
    participant7 = Participant.create({**parameter_dict})[0]
    participant8 = Participant.create({**parameter_dict})[0]
    participant9 = Participant.create({**parameter_dict})[0]
    participant10 = Participant.create({**parameter_dict})[0]
    
    # Link patients to participants and link participants to study
    patient1.ist_teilnehmer.connect(participant1, parameter_dict)
    patient2.ist_teilnehmer.connect(participant2, parameter_dict)
    patient3.ist_teilnehmer.connect(participant3, parameter_dict)
    patient4.ist_teilnehmer.connect(participant4, parameter_dict)
    patient5.ist_teilnehmer.connect(participant5, parameter_dict)
    patient6.ist_teilnehmer.connect(participant6, parameter_dict)
    patient7.ist_teilnehmer.connect(participant7, parameter_dict)
    patient8.ist_teilnehmer.connect(participant8, parameter_dict)
    patient9.ist_teilnehmer.connect(participant9, parameter_dict)
    patient10.ist_teilnehmer.connect(participant10, parameter_dict)
    
    studie0.hat_teilnehmer.connect(participant1, parameter_dict)
    studie0.hat_teilnehmer.connect(participant2, parameter_dict)
    studie0.hat_teilnehmer.connect(participant3, parameter_dict)
    studie0.hat_teilnehmer.connect(participant4, parameter_dict)
    studie0.hat_teilnehmer.connect(participant5, parameter_dict)
    studie0.hat_teilnehmer.connect(participant6, parameter_dict)
    studie0.hat_teilnehmer.connect(participant7, parameter_dict)
    studie0.hat_teilnehmer.connect(participant8, parameter_dict)
    studie0.hat_teilnehmer.connect(participant9, parameter_dict)
    studie0.hat_teilnehmer.connect(participant10, parameter_dict)
    
    # Create patient ids
    patient_idat_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "PatientIDAT")
    PatientIDAT = patient_idat_node.node_class
    
    patient_id_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "PatientID")
    PatientID = patient_id_node.node_class
    
    patient1_node_id = PatientID.create({**parameter_dict})[0]
    patient1_node_idat = PatientIDAT.create({**parameter_dict})[0]
    patient2_node_id = PatientID.create({**parameter_dict})[0]
    patient2_node_idat = PatientIDAT.create({**parameter_dict})[0]
    patient3_node_id = PatientID.create({**parameter_dict})[0]
    patient3_node_idat = PatientIDAT.create({**parameter_dict})[0]
    patient4_node_id = PatientID.create({**parameter_dict})[0]
    patient4_node_idat = PatientIDAT.create({**parameter_dict})[0]
    patient5_node_id = PatientID.create({**parameter_dict})[0]
    patient5_node_idat = PatientIDAT.create({**parameter_dict})[0]
    patient6_node_id = PatientID.create({**parameter_dict})[0]
    patient6_node_idat = PatientIDAT.create({**parameter_dict})[0]
    patient7_node_id = PatientID.create({**parameter_dict})[0]
    patient7_node_idat = PatientIDAT.create({**parameter_dict})[0]
    patient8_node_id = PatientID.create({**parameter_dict})[0]
    patient8_node_idat = PatientIDAT.create({**parameter_dict})[0]
    patient9_node_id = PatientID.create({**parameter_dict})[0]
    patient9_node_idat = PatientIDAT.create({**parameter_dict})[0]
    patient10_node_id = PatientID.create({**parameter_dict})[0]
    patient10_node_idat = PatientIDAT.create({**parameter_dict})[0]
    
    patient1_idat = DataNode.create({**parameter_dict, "value": "1"})[0]
    patient1_id = DataNode.create({**parameter_dict, "value": "1"})[0]
    patient2_idat = DataNode.create({**parameter_dict, "value": "2"})[0]
    patient2_id = DataNode.create({**parameter_dict, "value": "2"})[0]
    patient3_idat = DataNode.create({**parameter_dict, "value": "3"})[0]
    patient3_id = DataNode.create({**parameter_dict, "value": "3"})[0]
    patient4_idat = DataNode.create({**parameter_dict, "value": "4"})[0]
    patient4_id = DataNode.create({**parameter_dict, "value": "4"})[0]
    patient5_idat = DataNode.create({**parameter_dict, "value": "5"})[0]
    patient5_id = DataNode.create({**parameter_dict, "value": "5"})[0]
    patient6_idat = DataNode.create({**parameter_dict, "value": "6"})[0]
    patient6_id = DataNode.create({**parameter_dict, "value": "6"})[0]
    patient7_idat = DataNode.create({**parameter_dict, "value": "7"})[0]
    patient7_id = DataNode.create({**parameter_dict, "value": "7"})[0]
    patient8_idat = DataNode.create({**parameter_dict, "value": "8"})[0]
    patient8_id = DataNode.create({**parameter_dict, "value": "8"})[0]
    patient9_idat = DataNode.create({**parameter_dict, "value": "9"})[0]
    patient9_id = DataNode.create({**parameter_dict, "value": "9"})[0]
    patient10_idat = DataNode.create({**parameter_dict, "value": "10"})[0]
    patient10_id = DataNode.create({**parameter_dict, "value": "10"})[0]
    
    # Connect patient ids
    patient1.hat_patientid.connect(patient1_node_id, parameter_dict)
    patient1.hat_patientidat.connect(patient1_node_idat, parameter_dict)
    patient2.hat_patientid.connect(patient2_node_id, parameter_dict)
    patient2.hat_patientidat.connect(patient2_node_idat, parameter_dict)
    patient3.hat_patientid.connect(patient3_node_id, parameter_dict)
    patient3.hat_patientidat.connect(patient3_node_idat, parameter_dict)
    patient4.hat_patientid.connect(patient4_node_id, parameter_dict)
    patient4.hat_patientidat.connect(patient4_node_idat, parameter_dict)
    patient5.hat_patientid.connect(patient5_node_id, parameter_dict)
    patient5.hat_patientidat.connect(patient5_node_idat, parameter_dict)
    patient6.hat_patientid.connect(patient6_node_id, parameter_dict)
    patient6.hat_patientidat.connect(patient6_node_idat, parameter_dict)
    patient7.hat_patientid.connect(patient7_node_id, parameter_dict)
    patient7.hat_patientidat.connect(patient7_node_idat, parameter_dict)
    patient8.hat_patientid.connect(patient8_node_id, parameter_dict)
    patient8.hat_patientidat.connect(patient8_node_idat, parameter_dict)
    patient9.hat_patientid.connect(patient9_node_id, parameter_dict)
    patient9.hat_patientidat.connect(patient9_node_idat, parameter_dict)
    patient10.hat_patientid.connect(patient10_node_id, parameter_dict)
    patient10.hat_patientidat.connect(patient10_node_idat, parameter_dict)
    
    if SET_DATA_UNVERIFIED:
        patient1_node_id.in_review.connect(patient1_idat, parameter_dict)
        patient1_node_idat.in_review.connect(patient1_id, parameter_dict)
        patient2_node_id.in_review.connect(patient2_idat, parameter_dict)
        patient2_node_idat.in_review.connect(patient2_id, parameter_dict)
        patient3_node_id.in_review.connect(patient3_idat, parameter_dict)
        patient3_node_idat.in_review.connect(patient3_id, parameter_dict)
        patient4_node_id.in_review.connect(patient4_idat, parameter_dict)
        patient4_node_idat.in_review.connect(patient4_id, parameter_dict)
        patient5_node_id.in_review.connect(patient5_idat, parameter_dict)
        patient5_node_idat.in_review.connect(patient5_id, parameter_dict)
        patient6_node_id.in_review.connect(patient6_idat, parameter_dict)
        patient6_node_idat.in_review.connect(patient6_id, parameter_dict)
        patient7_node_id.in_review.connect(patient7_idat, parameter_dict)
        patient7_node_idat.in_review.connect(patient7_id, parameter_dict)
        patient8_node_id.in_review.connect(patient8_idat, parameter_dict)
        patient8_node_idat.in_review.connect(patient8_id, parameter_dict)
        patient9_node_id.in_review.connect(patient9_idat, parameter_dict)
        patient9_node_idat.in_review.connect(patient9_id, parameter_dict)
        patient10_node_id.in_review.connect(patient10_idat, parameter_dict)
        patient10_node_idat.in_review.connect(patient10_id, parameter_dict)
    else:
        patient1_node_id.current_data.connect(patient1_idat, parameter_dict)
        patient1_node_idat.current_data.connect(patient1_id, parameter_dict)
        patient2_node_id.current_data.connect(patient2_idat, parameter_dict)
        patient2_node_idat.current_data.connect(patient2_id, parameter_dict)
        patient3_node_id.current_data.connect(patient3_idat, parameter_dict)
        patient3_node_idat.current_data.connect(patient3_id, parameter_dict)
        patient4_node_id.current_data.connect(patient4_idat, parameter_dict)
        patient4_node_idat.current_data.connect(patient4_id, parameter_dict)
        patient5_node_id.current_data.connect(patient5_idat, parameter_dict)
        patient5_node_idat.current_data.connect(patient5_id, parameter_dict)
        patient6_node_id.current_data.connect(patient6_idat, parameter_dict)
        patient6_node_idat.current_data.connect(patient6_id, parameter_dict)
        patient7_node_id.current_data.connect(patient7_idat, parameter_dict)
        patient7_node_idat.current_data.connect(patient7_id, parameter_dict)
        patient8_node_id.current_data.connect(patient8_idat, parameter_dict)
        patient8_node_idat.current_data.connect(patient8_id, parameter_dict)
        patient9_node_id.current_data.connect(patient9_idat, parameter_dict)
        patient9_node_idat.current_data.connect(patient9_id, parameter_dict)
        patient10_node_id.current_data.connect(patient10_idat, parameter_dict)
        patient10_node_idat.current_data.connect(patient10_id, parameter_dict)
        
    # Create answers, answer groups and rowIDs
    answer_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Antwort")
    Answer = answer_node.node_class
    
    answer_group_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Antwortgruppe")
    AnswerGroup = answer_group_node.node_class
    
    answer_group_id_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "ReihenID")
    AnswerGroupID = answer_group_id_node.node_class
    
    patient1_answer_group = AnswerGroup.create({**parameter_dict})[0]
    patient2_answer_group = AnswerGroup.create({**parameter_dict})[0]
    patient3_answer_group = AnswerGroup.create({**parameter_dict})[0]
    patient4_answer_group = AnswerGroup.create({**parameter_dict})[0]
    patient5_answer_group = AnswerGroup.create({**parameter_dict})[0]
    patient6_answer_group = AnswerGroup.create({**parameter_dict})[0]
    patient7_answer_group = AnswerGroup.create({**parameter_dict})[0]
    patient8_answer_group = AnswerGroup.create({**parameter_dict})[0]
    patient9_answer_group = AnswerGroup.create({**parameter_dict})[0]
    patient10_answer_group = AnswerGroup.create({**parameter_dict})[0]
    
    patient1_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    patient2_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    patient3_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    patient4_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    patient5_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    patient6_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    patient7_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    patient8_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    patient9_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    patient10_answer_group_id = AnswerGroupID.create({**parameter_dict})[0]
    
    patient1_answer1 = Answer.create({**parameter_dict})[0]
    patient1_answer2 = Answer.create({**parameter_dict})[0]
    patient2_answer1 = Answer.create({**parameter_dict})[0]
    patient2_answer2 = Answer.create({**parameter_dict})[0]
    patient3_answer1 = Answer.create({**parameter_dict})[0]
    patient3_answer2 = Answer.create({**parameter_dict})[0]
    patient4_answer1 = Answer.create({**parameter_dict})[0]
    patient4_answer2 = Answer.create({**parameter_dict})[0]
    patient5_answer1 = Answer.create({**parameter_dict})[0]
    patient5_answer2 = Answer.create({**parameter_dict})[0]
    patient6_answer1 = Answer.create({**parameter_dict})[0]
    patient6_answer2 = Answer.create({**parameter_dict})[0]
    patient7_answer1 = Answer.create({**parameter_dict})[0]
    patient7_answer2 = Answer.create({**parameter_dict})[0]
    patient8_answer1 = Answer.create({**parameter_dict})[0]
    patient8_answer2 = Answer.create({**parameter_dict})[0]
    patient9_answer1 = Answer.create({**parameter_dict})[0]
    patient9_answer2 = Answer.create({**parameter_dict})[0]
    patient10_answer1 = Answer.create({**parameter_dict})[0]
    patient10_answer2 = Answer.create({**parameter_dict})[0]
    
    # Connect answers, answer groups and rowIDs
    participant1.gibt_antwortgruppe.connect(patient1_answer_group, parameter_dict)
    participant2.gibt_antwortgruppe.connect(patient2_answer_group, parameter_dict)
    participant3.gibt_antwortgruppe.connect(patient3_answer_group, parameter_dict)
    participant4.gibt_antwortgruppe.connect(patient4_answer_group, parameter_dict)
    participant5.gibt_antwortgruppe.connect(patient5_answer_group, parameter_dict)
    participant6.gibt_antwortgruppe.connect(patient6_answer_group, parameter_dict)
    participant7.gibt_antwortgruppe.connect(patient7_answer_group, parameter_dict)
    participant8.gibt_antwortgruppe.connect(patient8_answer_group, parameter_dict)
    participant9.gibt_antwortgruppe.connect(patient9_answer_group, parameter_dict)
    participant10.gibt_antwortgruppe.connect(patient10_answer_group, parameter_dict)
    
    patient1_answer_group.hat_reihenid.connect(patient1_answer_group_id, parameter_dict)
    patient2_answer_group.hat_reihenid.connect(patient2_answer_group_id, parameter_dict)
    patient3_answer_group.hat_reihenid.connect(patient3_answer_group_id, parameter_dict)
    patient4_answer_group.hat_reihenid.connect(patient4_answer_group_id, parameter_dict)
    patient5_answer_group.hat_reihenid.connect(patient5_answer_group_id, parameter_dict)
    patient6_answer_group.hat_reihenid.connect(patient6_answer_group_id, parameter_dict)
    patient7_answer_group.hat_reihenid.connect(patient7_answer_group_id, parameter_dict)
    patient8_answer_group.hat_reihenid.connect(patient8_answer_group_id, parameter_dict)
    patient9_answer_group.hat_reihenid.connect(patient9_answer_group_id, parameter_dict)
    patient10_answer_group.hat_reihenid.connect(patient10_answer_group_id, parameter_dict)

    patient1_answer_group.hat_antwort.connect(patient1_answer1, parameter_dict)
    patient1_answer_group.hat_antwort.connect(patient1_answer2, parameter_dict)
    patient2_answer_group.hat_antwort.connect(patient2_answer1, parameter_dict)
    patient2_answer_group.hat_antwort.connect(patient2_answer2, parameter_dict)
    patient3_answer_group.hat_antwort.connect(patient3_answer1, parameter_dict)
    patient3_answer_group.hat_antwort.connect(patient3_answer2, parameter_dict)
    patient4_answer_group.hat_antwort.connect(patient4_answer1, parameter_dict)
    patient4_answer_group.hat_antwort.connect(patient4_answer2, parameter_dict)
    patient5_answer_group.hat_antwort.connect(patient5_answer1, parameter_dict)
    patient5_answer_group.hat_antwort.connect(patient5_answer2, parameter_dict)
    patient6_answer_group.hat_antwort.connect(patient6_answer1, parameter_dict)
    patient6_answer_group.hat_antwort.connect(patient6_answer2, parameter_dict)
    patient7_answer_group.hat_antwort.connect(patient7_answer1, parameter_dict)
    patient7_answer_group.hat_antwort.connect(patient7_answer2, parameter_dict)
    patient8_answer_group.hat_antwort.connect(patient8_answer1, parameter_dict)
    patient8_answer_group.hat_antwort.connect(patient8_answer2, parameter_dict)
    patient9_answer_group.hat_antwort.connect(patient9_answer1, parameter_dict)
    patient9_answer_group.hat_antwort.connect(patient9_answer2, parameter_dict)
    patient10_answer_group.hat_antwort.connect(patient10_answer1, parameter_dict)
    patient10_answer_group.hat_antwort.connect(patient10_answer2, parameter_dict)
    
    item0.hat_antwort.connect(patient1_answer1, parameter_dict)
    item1.hat_antwort.connect(patient1_answer2, parameter_dict)
    item0.hat_antwort.connect(patient2_answer1, parameter_dict)
    item1.hat_antwort.connect(patient2_answer2, parameter_dict)
    item0.hat_antwort.connect(patient3_answer1, parameter_dict)
    item1.hat_antwort.connect(patient3_answer2, parameter_dict)
    item0.hat_antwort.connect(patient4_answer1, parameter_dict)
    item1.hat_antwort.connect(patient4_answer2, parameter_dict)
    item0.hat_antwort.connect(patient5_answer1, parameter_dict)
    item1.hat_antwort.connect(patient5_answer2, parameter_dict)
    item0.hat_antwort.connect(patient6_answer1, parameter_dict)
    item1.hat_antwort.connect(patient6_answer2, parameter_dict)
    item0.hat_antwort.connect(patient7_answer1, parameter_dict)
    item1.hat_antwort.connect(patient7_answer2, parameter_dict)
    item0.hat_antwort.connect(patient8_answer1, parameter_dict)
    item1.hat_antwort.connect(patient8_answer2, parameter_dict)
    item0.hat_antwort.connect(patient9_answer1, parameter_dict)
    item1.hat_antwort.connect(patient9_answer2, parameter_dict)
    item0.hat_antwort.connect(patient10_answer1, parameter_dict)
    item1.hat_antwort.connect(patient10_answer2, parameter_dict)
    
    # Add data quality check config and answer groups to questionnaire
    data_quality_check_config_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Qualitaetspruefung")
    DataQualityCheckConfig = data_quality_check_config_node.node_class
    data_quality_check_config = DataQualityCheckConfig.create({**parameter_dict})[0]
    
    empty_columns_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "LeereSpalten")
    EmptyColumns = empty_columns_node.node_class
    empty_columns = EmptyColumns.create({**parameter_dict})[0]
    
    empty_rows_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "LeereZeilen")
    EmptyRows = empty_rows_node.node_class
    empty_rows = EmptyRows.create({**parameter_dict})[0]
    
    empty_cells_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "LeereWerte")
    EmptyCells = empty_cells_node.node_class
    empty_cells = EmptyCells.create({**parameter_dict})[0]
    
    value_type_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Datentyp")
    ValueType = value_type_node.node_class
    value_type = ValueType.create({**parameter_dict})[0]
    
    value_range_min_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Minimum")
    ValueRangeMin = value_range_min_node.node_class
    value_range_min = ValueRangeMin.create({**parameter_dict})[0]
    
    value_range_max_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Maximum")
    ValueRangeMax = value_range_max_node.node_class
    value_range_max = ValueRangeMax.create({**parameter_dict})[0]
    
    value_required_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "BenoetigtQualitaetspruefung")
    ValueRequired = value_required_node.node_class
    value_required = ValueRequired.create({**parameter_dict})[0]
    
    value_mapping_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "Auswahlmoeglichkeiten")
    ValueMapping = value_mapping_node.node_class
    value_mapping = ValueMapping.create({**parameter_dict})[0]
    
    mapping_separator_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "TrennzeichenAuswahlmoeglichkeiten")
    MappingSeparator = mapping_separator_node.node_class
    mapping_separator = MappingSeparator.create({**parameter_dict})[0]
    
    answer_separator_node: OntologyNode = OntologyNode.nodes.first_or_none(tag = "TrennzeichenAntworten")
    AnswerSeparator = answer_separator_node.node_class
    answer_separator = AnswerSeparator.create({**parameter_dict})[0]
    
    fragebogen0.hat_qualitaetspruefung.connect(data_quality_check_config, parameter_dict)
    data_quality_check_config.hat_leerespalten.connect(empty_columns, parameter_dict)
    data_quality_check_config.hat_leerezeilen.connect(empty_rows, parameter_dict)
    data_quality_check_config.hat_leerewerte.connect(empty_cells, parameter_dict)
    data_quality_check_config.hat_datentyp.connect(value_type, parameter_dict)
    data_quality_check_config.hat_minimum.connect(value_range_min, parameter_dict)
    data_quality_check_config.hat_maximum.connect(value_range_max, parameter_dict)
    data_quality_check_config.hat_benoetigtqualitaetspruefung.connect(value_required, parameter_dict)
    data_quality_check_config.hat_auswahlmoeglichkeiten.connect(value_mapping, parameter_dict)
    data_quality_check_config.hat_trennzeichenauswahlmoeglichkeiten.connect(mapping_separator, parameter_dict)
    data_quality_check_config.hat_trennzeichenantworten.connect(answer_separator, parameter_dict)
    
    empty_columns_data = DataNode.create({**parameter_dict, "value": "True"})[0]
    empty_rows_data = DataNode.create({**parameter_dict, "value": "True"})[0]
    empty_cells_data = DataNode.create({**parameter_dict, "value": "False"})[0]
    value_type_data = DataNode.create({**parameter_dict, "value": "Datentyp"})[0]
    value_range_min_data = DataNode.create({**parameter_dict, "value": "Minimum"})[0]
    value_range_max_data = DataNode.create({**parameter_dict, "value": "Maximum"})[0]
    value_required_data = DataNode.create({**parameter_dict, "value": "Benoetigt"})[0]
    value_mapping_data = DataNode.create({**parameter_dict, "value": "Antwortmoeglichkeiten"})[0]
    mapping_separator_data = DataNode.create({**parameter_dict, "value": "SEMICOLON"})[0]
    answer_separator_data = DataNode.create({**parameter_dict, "value": "COMMA"})[0]
    
    if SET_DATA_UNVERIFIED:
        empty_columns.in_review.connect(empty_columns_data, parameter_dict)
        empty_rows.in_review.connect(empty_rows_data, parameter_dict)
        empty_cells.in_review.connect(empty_cells_data, parameter_dict)
        value_type.in_review.connect(value_type_data, parameter_dict)
        value_range_min.in_review.connect(value_range_min_data, parameter_dict)
        value_range_max.in_review.connect(value_range_max_data, parameter_dict)
        value_required.in_review.connect(value_required_data, parameter_dict)
        value_mapping.in_review.connect(value_mapping_data, parameter_dict)
        mapping_separator.in_review.connect(mapping_separator_data, parameter_dict)
        answer_separator.in_review.connect(answer_separator_data, parameter_dict)
    else:
        empty_columns.current_data.connect(empty_columns_data, parameter_dict)
        empty_rows.current_data.connect(empty_rows_data, parameter_dict)
        empty_cells.current_data.connect(empty_cells_data, parameter_dict)
        value_type.current_data.connect(value_type_data, parameter_dict)
        value_range_min.current_data.connect(value_range_min_data, parameter_dict)
        value_range_max.current_data.connect(value_range_max_data, parameter_dict)
        value_required.current_data.connect(value_required_data, parameter_dict)
        value_mapping.current_data.connect(value_mapping_data, parameter_dict)
        mapping_separator.current_data.connect(mapping_separator_data, parameter_dict)
        answer_separator.current_data.connect(answer_separator_data, parameter_dict)
    
    fragebogen0.hat_antwortgruppe.connect(patient1_answer_group, parameter_dict)
    fragebogen0.hat_antwortgruppe.connect(patient2_answer_group, parameter_dict)
    fragebogen0.hat_antwortgruppe.connect(patient3_answer_group, parameter_dict)
    fragebogen0.hat_antwortgruppe.connect(patient4_answer_group, parameter_dict)
    fragebogen0.hat_antwortgruppe.connect(patient5_answer_group, parameter_dict)
    fragebogen0.hat_antwortgruppe.connect(patient6_answer_group, parameter_dict)
    fragebogen0.hat_antwortgruppe.connect(patient7_answer_group, parameter_dict)
    fragebogen0.hat_antwortgruppe.connect(patient8_answer_group, parameter_dict)
    fragebogen0.hat_antwortgruppe.connect(patient9_answer_group, parameter_dict)
    fragebogen0.hat_antwortgruppe.connect(patient10_answer_group, parameter_dict)
    
    # Create and connect data nodes for answer and rowID
    patient1_answer_group_id_data = DataNode.create({**parameter_dict, "value": "1"})[0]
    patient2_answer_group_id_data = DataNode.create({**parameter_dict, "value": "2"})[0]
    patient3_answer_group_id_data = DataNode.create({**parameter_dict, "value": "3"})[0]
    patient4_answer_group_id_data = DataNode.create({**parameter_dict, "value": "4"})[0]
    patient5_answer_group_id_data = DataNode.create({**parameter_dict, "value": "5"})[0]
    patient6_answer_group_id_data = DataNode.create({**parameter_dict, "value": "6"})[0]
    patient7_answer_group_id_data = DataNode.create({**parameter_dict, "value": "7"})[0]
    patient8_answer_group_id_data = DataNode.create({**parameter_dict, "value": "8"})[0]
    patient9_answer_group_id_data = DataNode.create({**parameter_dict, "value": "9"})[0]
    patient10_answer_group_id_data = DataNode.create({**parameter_dict, "value": "10"})[0]
    
    patient1_answer1_data= DataNode.create({**parameter_dict, "value": "1"})[0]
    patient1_answer2_data= DataNode.create({**parameter_dict, "value": "19"})[0]
    patient2_answer1_data= DataNode.create({**parameter_dict, "value": "2"})[0]
    patient2_answer2_data= DataNode.create({**parameter_dict, "value": "54"})[0]
    patient3_answer1_data= DataNode.create({**parameter_dict, "value": "3"})[0]
    patient3_answer2_data= DataNode.create({**parameter_dict, "value": "34"})[0]
    patient4_answer1_data= DataNode.create({**parameter_dict, "value": "4"})[0]
    patient4_answer2_data= DataNode.create({**parameter_dict, "value": "75"})[0]
    patient5_answer1_data= DataNode.create({**parameter_dict, "value": "5"})[0]
    patient5_answer2_data= DataNode.create({**parameter_dict, "value": "64"})[0]
    patient6_answer1_data= DataNode.create({**parameter_dict, "value": "6"})[0]
    patient6_answer2_data= DataNode.create({**parameter_dict, "value": "34"})[0]
    patient7_answer1_data= DataNode.create({**parameter_dict, "value": "7"})[0]
    patient7_answer2_data= DataNode.create({**parameter_dict, "value": "44"})[0]
    patient8_answer1_data= DataNode.create({**parameter_dict, "value": "8"})[0]
    patient8_answer2_data= DataNode.create({**parameter_dict, "value": "92"})[0]
    patient9_answer1_data= DataNode.create({**parameter_dict, "value": "9"})[0]
    patient9_answer2_data= DataNode.create({**parameter_dict, "value": "18"})[0]
    patient10_answer1_data = DataNode.create({**parameter_dict, "value": "10"})[0]
    patient10_answer2_data = DataNode.create({**parameter_dict, "value": "78"})[0]
    
    if SET_DATA_UNVERIFIED:
        patient1_answer_group_id.in_review.connect(patient1_answer_group_id_data, parameter_dict)
        patient2_answer_group_id.in_review.connect(patient2_answer_group_id_data, parameter_dict)
        patient3_answer_group_id.in_review.connect(patient3_answer_group_id_data, parameter_dict)
        patient4_answer_group_id.in_review.connect(patient4_answer_group_id_data, parameter_dict)
        patient5_answer_group_id.in_review.connect(patient5_answer_group_id_data, parameter_dict)
        patient6_answer_group_id.in_review.connect(patient6_answer_group_id_data, parameter_dict)
        patient7_answer_group_id.in_review.connect(patient7_answer_group_id_data, parameter_dict)
        patient8_answer_group_id.in_review.connect(patient8_answer_group_id_data, parameter_dict)
        patient9_answer_group_id.in_review.connect(patient9_answer_group_id_data, parameter_dict)
        patient10_answer_group_id.in_review.connect(patient10_answer_group_id_data, parameter_dict)
        
        patient1_answer1.in_review.connect(patient1_answer1_data, parameter_dict)
        patient1_answer2.in_review.connect(patient1_answer2_data, parameter_dict)
        patient2_answer1.in_review.connect(patient2_answer1_data, parameter_dict)
        patient2_answer2.in_review.connect(patient2_answer2_data, parameter_dict)
        patient3_answer1.in_review.connect(patient3_answer1_data, parameter_dict)
        patient3_answer2.in_review.connect(patient3_answer2_data, parameter_dict)
        patient4_answer1.in_review.connect(patient4_answer1_data, parameter_dict)
        patient4_answer2.in_review.connect(patient4_answer2_data, parameter_dict)
        patient5_answer1.in_review.connect(patient5_answer1_data, parameter_dict)
        patient5_answer2.in_review.connect(patient5_answer2_data, parameter_dict)
        patient6_answer1.in_review.connect(patient6_answer1_data, parameter_dict)
        patient6_answer2.in_review.connect(patient6_answer2_data, parameter_dict)
        patient7_answer1.in_review.connect(patient7_answer1_data, parameter_dict)
        patient7_answer2.in_review.connect(patient7_answer2_data, parameter_dict)
        patient8_answer1.in_review.connect(patient8_answer1_data, parameter_dict)
        patient8_answer2.in_review.connect(patient8_answer2_data, parameter_dict)
        patient9_answer1.in_review.connect(patient9_answer1_data, parameter_dict)
        patient9_answer2.in_review.connect(patient9_answer2_data, parameter_dict)
        patient10_answer1.in_review.connect(patient10_answer1_data, parameter_dict)
        patient10_answer2.in_review.connect(patient10_answer2_data, parameter_dict)
    else:
        patient1_answer_group_id.current_data.connect(patient1_answer_group_id_data, parameter_dict)
        patient2_answer_group_id.current_data.connect(patient2_answer_group_id_data, parameter_dict)
        patient3_answer_group_id.current_data.connect(patient3_answer_group_id_data, parameter_dict)
        patient4_answer_group_id.current_data.connect(patient4_answer_group_id_data, parameter_dict)
        patient5_answer_group_id.current_data.connect(patient5_answer_group_id_data, parameter_dict)
        patient6_answer_group_id.current_data.connect(patient6_answer_group_id_data, parameter_dict)
        patient7_answer_group_id.current_data.connect(patient7_answer_group_id_data, parameter_dict)
        patient8_answer_group_id.current_data.connect(patient8_answer_group_id_data, parameter_dict)
        patient9_answer_group_id.current_data.connect(patient9_answer_group_id_data, parameter_dict)
        patient10_answer_group_id.current_data.connect(patient10_answer_group_id_data, parameter_dict)
        
        patient1_answer1.current_data.connect(patient1_answer1_data, parameter_dict)
        patient1_answer2.current_data.connect(patient1_answer2_data, parameter_dict)
        patient2_answer1.current_data.connect(patient2_answer1_data, parameter_dict)
        patient2_answer2.current_data.connect(patient2_answer2_data, parameter_dict)
        patient3_answer1.current_data.connect(patient3_answer1_data, parameter_dict)
        patient3_answer2.current_data.connect(patient3_answer2_data, parameter_dict)
        patient4_answer1.current_data.connect(patient4_answer1_data, parameter_dict)
        patient4_answer2.current_data.connect(patient4_answer2_data, parameter_dict)
        patient5_answer1.current_data.connect(patient5_answer1_data, parameter_dict)
        patient5_answer2.current_data.connect(patient5_answer2_data, parameter_dict)
        patient6_answer1.current_data.connect(patient6_answer1_data, parameter_dict)
        patient6_answer2.current_data.connect(patient6_answer2_data, parameter_dict)
        patient7_answer1.current_data.connect(patient7_answer1_data, parameter_dict)
        patient7_answer2.current_data.connect(patient7_answer2_data, parameter_dict)
        patient8_answer1.current_data.connect(patient8_answer1_data, parameter_dict)
        patient8_answer2.current_data.connect(patient8_answer2_data, parameter_dict)
        patient9_answer1.current_data.connect(patient9_answer1_data, parameter_dict)
        patient9_answer2.current_data.connect(patient9_answer2_data, parameter_dict)
        patient10_answer1.current_data.connect(patient10_answer1_data, parameter_dict)
        patient10_answer2.current_data.connect(patient10_answer2_data, parameter_dict)