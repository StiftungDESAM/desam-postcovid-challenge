from neomodel.sync_.core import db
from .models import OntologyNode, OntologyNodeTypes, OntologyRelationship

from knowledge.models import load_all_knowledge_node_classes
from typing import List
import logging
from ontology.diff import Entity
import re
from ontology.utils import get_all_outgoing_relationships

import re
import uuid
from.diff import UMLAUTS_MAPPING
from study.models import Study, CodeBookColumn
from datetime import datetime
from graph_migrations.studies import load_migrations
logger = logging.getLogger(__name__) 
def get_all_nodes() -> List[OntologyNode]:
    return OntologyNode.nodes.all()

def delete_all_nodes(request) -> None:
    return db.cypher_query("MATCH (n:OntologyNode) DETACH DELETE n")

def create_nodes(request, count: int) -> List[OntologyNode]:
    # Defines three different nodes types for testing.
    stakeholder = {
        "name": "Patient",
        "tag": "Patient",
        "node_type": OntologyNodeTypes.STAKEHOLDER
    }

    connection = {
        "name": "Lab result",
        "tag": "LabResult",
        "node_type": OntologyNodeTypes.CONNECTIVE
    }

    leaves = [
        {
            "name": f"Leaf node {i}", 
            "tag": f"LeafNode{i}", 
            "node_type": OntologyNodeTypes.LEAF
        }
        for i in range(count-2)
    ]

    # Creates of the nodes.
    stakeholder_node: OntologyNode = OntologyNode.create(stakeholder)[0]
    connective_node: OntologyNode = OntologyNode.create(connection)[0]
    leaf_nodes: List[OntologyNode] = OntologyNode.create(*leaves)

    # Connects the stkakeholder node to the connective node.
    stakeholder_node.children.connect(
        node = connective_node,
        properties = {
            "name": "HAS",
            "tag": stakeholder_node.tag.upper() + "_HAS_" + connective_node.tag.upper()
        }
    )

    # Connects all leaf nodes to the connective node.
    for leaf_node in leaf_nodes:
        properties = {
            "name": "CONTAINS",
            "tag": connective_node.tag.upper() + "_CONTAINS_" + leaf_node.tag.upper()
        }
        connective_node.children.connect(leaf_node, properties)

    new_nodes = [stakeholder_node, connective_node] + leaf_nodes

    # When new ontology nodes are created, the knowledge node classes must be reloaded so that the new classes are created.
    load_all_knowledge_node_classes()
    return new_nodes



def normalize_string(text: str) -> str:
    # Ersetze Umlaute
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
        'ß': 'ss'
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # Entferne Sonderzeichen (alles außer Buchstaben, Zahlen und _-)
    text = re.sub(r'[^a-zA-Z0-9_-]', '', text)

    return text


def get_ontology_triplets(transform=True, nodes = None):
    entities: dict[str, Entity] = {}
    if nodes is None:
        nodes = get_all_nodes()

    id_counter=0
    node_id_counter = 0
    rel_id_counter= 0
    #elementid to node id
    element_id: dict[str,str]={}
    for n in nodes:
        node_id = "node#" + str(node_id_counter)
        #load name, tag, updated_at and created_at + id
        entity = Entity(subject=node_id)
        entity.name = normalize_string(n.name)
        entity.id = str(node_id_counter)
        if(n.node_type==OntologyNodeTypes.STAKEHOLDER): 
            entity.properties["is_stakeholder"]= "true"
            entity.properties["is_leaf"] = "false"
        elif(n.node_type==OntologyNodeTypes.CONNECTIVE): 
            entity.properties["is_stakeholder"]= "false"
            entity.properties["is_leaf"] = "false"
        elif(n.node_type==OntologyNodeTypes.LEAF): 
            entity.properties["is_stakeholder"]= "false"
            entity.properties["is_leaf"] = "true"
        entity.properties["updated_at"]=n.updated_at
        entity.properties["created_at"]=n.created_at
        entity.properties["tag"]=n.tag
        entity.properties["name"]=n.name
        entities[node_id]= entity
        element_id[n.element_id]=node_id
        if(n.name == "Metadaten" and transform==False):
            meta_id = node_id
            
        id_counter+=1
        node_id_counter+=1
        #rels = get_all_outgoing_relationships(n,label = OntologyNode.get_relationship_label())
    #hate doing it like this but iterate over all rels 
    node_id_counter=0
    for n in nodes:
        rels = get_all_outgoing_relationships(n,label = OntologyNode.get_relationship_label())
        node_id = "node#" + str(node_id_counter)
        for rel in rels:
            rel_id= "relationship#"+str(rel_id_counter)
            entity = Entity(subject=rel_id)
            entity.name = normalize_string(rel.relationship.name)
            entity.id = str(id_counter)
            entity.source = entities[node_id]

            target_node = element_id.get(rel.end_node.element_id_property)
            if target_node is None:
                continue # Connections to nodes that are not in the export node-set are skipped.

            entity.target = entities[target_node]
            entity.properties["tag"]=str(rel.relationship.tag)
            entity.properties["cardinality"]= rel.relationship.cardinality
            entity.properties["last_updated"]=rel.relationship.updated_at
            entity.properties["created_at"]=rel.relationship.created_at
            entity.properties["name"]=rel.relationship.name
            entities[rel_id]=entity
            rel_id_counter+=1
            id_counter+=1
        node_id_counter+=1

    if transform:
        return list(entities.values())
    else:
        return entities, id_counter, node_id_counter,rel_id_counter,meta_id
    
def generate_tag_name(column_name: str):
    """Replaces certain special characters like äöüß with ascii and removes all special characters, including spaces."""
    name = column_name.translate(UMLAUTS_MAPPING)
    return re.sub("[^A-Za-z]+", "", name)


def get_codebooks_for_rdf(study: Study):

    entities, id_counter,node_id_counter,rel_id_counter,meta_id= get_ontology_triplets(transform=False)

    migrations = load_migrations(study)

    i=0
    for m in migrations:
         node_id = "node#" + str(node_id_counter+i)
         entity_node= Entity(subject=node_id)
         entity_node.name = normalize_string(m.new_node.properties["name"])
         entity_node.id = str(node_id_counter+i)
         entity_node.properties["is_stakeholder"]= "false"
         entity_node.properties["is_leaf"] = "true"
         entity_node.properties["updated_at"]=datetime.now().isoformat()
         entity_node.properties["created_at"]=datetime.now().isoformat()
         entity_node.properties["tag"]=normalize_string(m.new_node.properties["tag"])
         entity_node.properties["name"]=normalize_string(m.new_node.properties["name"])
         entity_node.diff["added"] = True
         entities[node_id]= entity_node
        
         rel_id= "relationship#"+str(rel_id_counter+i)
         entity_rel = Entity(subject=rel_id)
         entity_rel.name = normalize_string(m.new_relationship.properties["name"])
         entity_rel.id = str(id_counter+i)
         
         entity_rel.source = entities[meta_id]
         #target_node= element_id[rel.end_node.element_id_property]
         #logger.debug(f"metadata entity {entities[meta_id]}")
         entity_rel.target = entities[node_id]

         entity_rel.properties["tag"]=m.new_relationship.properties["tag"]
         entity_rel.properties["cardinality"]= m.new_relationship.properties["cardinality"]
         entity_rel.properties["last_updated"]=datetime.now().isoformat()
         entity_rel.properties["created_at"]=datetime.now().isoformat()
         entity_rel.properties["name"]=normalize_string(m.new_relationship.properties["name"])
         entity_rel.diff["added"] = True
         entities[rel_id]=entity_rel
         i+=1


    return list(entities.values())

    
def create_example_ontology():
    forschung: OntologyNode = OntologyNode(tag="Forschung", name="Forschung", node_type=OntologyNodeTypes.STAKEHOLDER).save()
    studie: OntologyNode = OntologyNode(tag="Studie", name="Studie", node_type=OntologyNodeTypes.CONNECTIVE).save()
    teilnehmer: OntologyNode = OntologyNode(tag="Teilnehmer", name="Teilnehmer", node_type=OntologyNodeTypes.CONNECTIVE).save()
    datenerhebung: OntologyNode = OntologyNode(tag="Datenerhebung", name="Datenerhebung", node_type=OntologyNodeTypes.CONNECTIVE).save()
    fragebogen: OntologyNode = OntologyNode(tag="Fragebogen", name="Fragebogen", node_type=OntologyNodeTypes.CONNECTIVE).save()
    item: OntologyNode = OntologyNode(tag="Item", name="Item", node_type=OntologyNodeTypes.CONNECTIVE).save()
    metadaten: OntologyNode = OntologyNode(tag="Metadaten", name="Metadaten", node_type=OntologyNodeTypes.CONNECTIVE).save()
    leistungserbringer: OntologyNode = OntologyNode(tag="Leistungserbringer", name="Leistungserbringer", node_type=OntologyNodeTypes.STAKEHOLDER).save()
    antwort: OntologyNode = OntologyNode(tag="Antwort", name="Antwort", node_type=OntologyNodeTypes.LEAF).save()
    feldtyp: OntologyNode = OntologyNode(tag="Feldtyp", name="Feldtyp", node_type=OntologyNodeTypes.LEAF).save()
    benötigt: OntologyNode = OntologyNode(tag="Benötigt", name="Benötigt", node_type=OntologyNodeTypes.LEAF).save()
    frage: OntologyNode = OntologyNode(tag="Frage", name="Frage", node_type=OntologyNodeTypes.LEAF).save()
    feldname: OntologyNode = OntologyNode(tag="Feldname", name="Feldname", node_type=OntologyNodeTypes.LEAF).save()
    sektionsüberschrift: OntologyNode = OntologyNode(tag="Sektionsüberschrift", name="Sektionsüberschrift", node_type=OntologyNodeTypes.LEAF).save()
    mapping: OntologyNode = OntologyNode(tag="Mapping", name="Mapping", node_type=OntologyNodeTypes.LEAF).save()

    forschung.children.connect(studie, {"tag": 1001, "name": "erstellt", "cardinality": "n"})
    studie.children.connect(teilnehmer, {"tag": 1002, "name": "hat", "cardinality": "n"})
    leistungserbringer.children.connect(teilnehmer, {"tag": 1003, "name": "ist", "cardinality": "n"})
    teilnehmer.children.connect(antwort, {"tag": 1004, "name": "gibt", "cardinality": "n"})
    studie.children.connect(datenerhebung, {"tag": 1005, "name": "hat", "cardinality": "n"})
    datenerhebung.children.connect(fragebogen, {"tag": 1006, "name": "hat", "cardinality": "n"})
    fragebogen.children.connect(item, {"tag": 1007, "name": "hat", "cardinality": "n"})
    item.children.connect(antwort, {"tag": 1008, "name": "hat", "cardinality": "n"})
    item.children.connect(metadaten, {"tag": 1009, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(feldtyp, {"tag": 1010, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(benötigt, {"tag": 1011, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(frage, {"tag": 1012, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(feldname, {"tag": 1013, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(sektionsüberschrift, {"tag": 1014, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(mapping, {"tag": 1015, "name": "hat", "cardinality": "n"})

    return [
        forschung, studie, teilnehmer, datenerhebung, fragebogen, item, metadaten, leistungserbringer, antwort, feldtyp, benötigt, frage, feldname, sektionsüberschrift, mapping
    ]
    
    
    
def create_baseline_ontology():
    forschung: OntologyNode = OntologyNode(tag="Forschung", name="Forschung", node_type=OntologyNodeTypes.STAKEHOLDER).save()
    studie: OntologyNode = OntologyNode(tag="Studie", name="Studie", node_type=OntologyNodeTypes.CONNECTIVE).save()
    teilnehmer: OntologyNode = OntologyNode(tag="Teilnehmer", name="Teilnehmer", node_type=OntologyNodeTypes.CONNECTIVE).save()
    studieninformationen: OntologyNode = OntologyNode(tag="Studieninformationen", name="Studieninformationen", node_type=OntologyNodeTypes.CONNECTIVE).save()
    startdatum: OntologyNode = OntologyNode(tag="Startdatum", name="Startdatum", node_type=OntologyNodeTypes.LEAF).save()
    enddatum: OntologyNode = OntologyNode(tag="Enddatum", name="Enddatum", node_type=OntologyNodeTypes.LEAF).save()
    studien_id: OntologyNode = OntologyNode(tag="StudienID", name="Studien-ID", node_type=OntologyNodeTypes.LEAF).save()
    studienname: OntologyNode = OntologyNode(tag="Studienname", name="Studienname", node_type=OntologyNodeTypes.LEAF).save()
    beschreibungstext: OntologyNode = OntologyNode(tag="Beschreibungstext", name="Beschreibungstext", node_type=OntologyNodeTypes.LEAF).save()
    drks_id: OntologyNode = OntologyNode(tag="DRKSID", name="DRKS-ID", node_type=OntologyNodeTypes.LEAF).save()
    studienzweck: OntologyNode = OntologyNode(tag="Studienzweck", name="Studienzweck", node_type=OntologyNodeTypes.LEAF).save()
    
    datenerhebung: OntologyNode = OntologyNode(tag="Datenerhebung", name="Datenerhebung", node_type=OntologyNodeTypes.CONNECTIVE).save()
    fragebogen: OntologyNode = OntologyNode(tag="Fragebogen", name="Fragebogen", node_type=OntologyNodeTypes.CONNECTIVE).save()
    fragebogen_id: OntologyNode = OntologyNode(tag="FragebogenID", name="Fragebogen-ID", node_type=OntologyNodeTypes.LEAF).save()
    fragebogen_name: OntologyNode = OntologyNode(tag="Fragebogenname", name="Fragebogenname", node_type=OntologyNodeTypes.LEAF).save()
    antwortgruppe: OntologyNode = OntologyNode(tag="Antwortgruppe", name="Antwortgruppe", node_type=OntologyNodeTypes.CONNECTIVE).save()
    reihen_id: OntologyNode = OntologyNode(tag="ReihenID", name="Reihen ID", node_type=OntologyNodeTypes.LEAF).save()
    spalten_id: OntologyNode = OntologyNode(tag="SpaltenID", name="Spalten ID", node_type=OntologyNodeTypes.LEAF).save()
    
    qualitätsprüfung: OntologyNode = OntologyNode(tag="Qualitaetspruefung", name="Qualitätsprüfung", node_type=OntologyNodeTypes.CONNECTIVE).save()
    datentyp : OntologyNode = OntologyNode(tag="Datentyp", name="Datentyp", node_type=OntologyNodeTypes.LEAF).save()
    minimum: OntologyNode = OntologyNode(tag="Minimum", name="Minimum", node_type=OntologyNodeTypes.LEAF).save()
    maximum: OntologyNode = OntologyNode(tag="Maximum", name="Maximum", node_type=OntologyNodeTypes.LEAF).save()
    auswahlmöglichkeiten: OntologyNode = OntologyNode(tag="Auswahlmoeglichkeiten", name="Auswahlmöglichkeiten", node_type=OntologyNodeTypes.LEAF).save()
    trennzeichen_auswahlmöglichkeiten: OntologyNode = OntologyNode(tag="TrennzeichenAuswahlmoeglichkeiten", name="Trennzeichen Auswahlmöglichkeiten", node_type=OntologyNodeTypes.LEAF).save()
    trennzeichen_antworten: OntologyNode = OntologyNode(tag="TrennzeichenAntworten", name="Trennzeichen Antworten", node_type=OntologyNodeTypes.LEAF).save()
    benötigt_qualitätsprüfung: OntologyNode = OntologyNode(tag="BenoetigtQualitaetspruefung", name="Benötigt Qualitätsprüfung", node_type=OntologyNodeTypes.LEAF).save()
    leere_werte: OntologyNode = OntologyNode(tag="LeereWerte", name="Leere Werte", node_type=OntologyNodeTypes.LEAF).save()
    leere_zeilen: OntologyNode = OntologyNode(tag="LeereZeilen", name="Leere Zeilen", node_type=OntologyNodeTypes.LEAF).save()
    leere_spalten: OntologyNode = OntologyNode(tag="LeereSpalten", name="Leere Spalten", node_type=OntologyNodeTypes.LEAF).save()
    
    item: OntologyNode = OntologyNode(tag="Item", name="Item", node_type=OntologyNodeTypes.CONNECTIVE).save()
    metadaten: OntologyNode = OntologyNode(tag="Metadaten", name="Metadaten", node_type=OntologyNodeTypes.CONNECTIVE).save()
    leistungserbringer: OntologyNode = OntologyNode(tag="Leistungserbringer", name="Leistungserbringer", node_type=OntologyNodeTypes.STAKEHOLDER).save()
    antwort: OntologyNode = OntologyNode(tag="Antwort", name="Antwort", node_type=OntologyNodeTypes.LEAF).save()
    #feldtyp: OntologyNode = OntologyNode(tag="Feldtyp", name="Feldtyp", node_type=OntologyNodeTypes.LEAF).save()
    #benötigt: OntologyNode = OntologyNode(tag="Benötigt", name="Benötigt", node_type=OntologyNodeTypes.LEAF).save()
    #frage: OntologyNode = OntologyNode(tag="Frage", name="Frage", node_type=OntologyNodeTypes.LEAF).save()
    feldname: OntologyNode = OntologyNode(tag="Feldname", name="Feldname", node_type=OntologyNodeTypes.LEAF).save()
    #sektionsüberschrift: OntologyNode = OntologyNode(tag="Sektionsüberschrift", name="Sektionsüberschrift", node_type=OntologyNodeTypes.LEAF).save()
    #mapping: OntologyNode = OntologyNode(tag="Mapping", name="Mapping", node_type=OntologyNodeTypes.LEAF).save()
    verknüpftes_item_id: OntologyNode = OntologyNode(tag="VerknuepftesItemID", name="Verknüpftes Item ID", node_type=OntologyNodeTypes.LEAF).save()
    # einheit: OntologyNode = OntologyNode(tag="Einheit", name="Einheit", node_type=OntologyNodeTypes.LEAF).save()
    
    patient: OntologyNode = OntologyNode(tag="Patient", name="Patient", node_type=OntologyNodeTypes.STAKEHOLDER).save()
    patient_idat: OntologyNode = OntologyNode(tag="PatientIDAT", name="Patient IDAT", node_type=OntologyNodeTypes.LEAF).save()
    patient_id: OntologyNode = OntologyNode(tag="PatientID", name="Patient ID", node_type=OntologyNodeTypes.LEAF).save()
    

    forschung.children.connect(studie, {"tag": 1001, "name": "erstellt", "cardinality": "n"})
    studie.children.connect(teilnehmer, {"tag": 1002, "name": "hat", "cardinality": "n"})
    leistungserbringer.children.connect(teilnehmer, {"tag": 1003, "name": "ist", "cardinality": "n"})
    teilnehmer.children.connect(antwortgruppe, {"tag": 1004, "name": "gibt", "cardinality": "n"})
    studie.children.connect(datenerhebung, {"tag": 1005, "name": "hat", "cardinality": "n"})
    datenerhebung.children.connect(fragebogen, {"tag": 1006, "name": "hat", "cardinality": "n"})
    fragebogen.children.connect(item, {"tag": 1007, "name": "hat", "cardinality": "n"})
    item.children.connect(antwort, {"tag": 1008, "name": "hat", "cardinality": "n"})
    item.children.connect(spalten_id, {"tag": 1045, "name": "hat", "cardinality": "1"})
    
    item.children.connect(metadaten, {"tag": 1009, "name": "hat", "cardinality": "n"})
    #metadaten.children.connect(feldtyp, {"tag": 1010, "name": "hat", "cardinality": "n"})
    #metadaten.children.connect(benötigt, {"tag": 1011, "name": "hat", "cardinality": "n"})
    #metadaten.children.connect(frage, {"tag": 1012, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(feldname, {"tag": 1013, "name": "hat", "cardinality": "1"})
    #metadaten.children.connect(sektionsüberschrift, {"tag": 1014, "name": "hat", "cardinality": "n"})
    #metadaten.children.connect(mapping, {"tag": 1015, "name": "hat", "cardinality": "n"})
    
    studie.children.connect(studieninformationen, {"tag": 1016, "name": "hat", "cardinality": "1"})
    studieninformationen.children.connect(startdatum, {"tag": 1017, "name": "hat", "cardinality": "1"})
    studieninformationen.children.connect(enddatum, {"tag": 1018, "name": "hat", "cardinality": "1"})
    studieninformationen.children.connect(studien_id, {"tag": 1019, "name": "hat", "cardinality": "1"})
    studieninformationen.children.connect(studienname, {"tag": 1020, "name": "hat", "cardinality": "1"})
    studieninformationen.children.connect(beschreibungstext, {"tag": 1021, "name": "hat", "cardinality": "1"})
    studieninformationen.children.connect(drks_id, {"tag": 1022, "name": "hat", "cardinality": "1"})
    studieninformationen.children.connect(studienzweck, {"tag": 1023, "name": "hat", "cardinality": "1"})
    
    fragebogen.children.connect(fragebogen_id, {"tag": 1024, "name": "hat", "cardinality": "1"})
    fragebogen.children.connect(fragebogen_name, {"tag": 1025, "name": "hat", "cardinality": "1"})
    fragebogen.children.connect(antwortgruppe, {"tag": 1026, "name": "hat", "cardinality": "n"})
    fragebogen.children.connect(qualitätsprüfung, {"tag": 1027, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(datentyp, {"tag": 1028, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(minimum, {"tag": 1029, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(maximum, {"tag": 1030, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(auswahlmöglichkeiten, {"tag": 1031, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(trennzeichen_auswahlmöglichkeiten, {"tag": 1032, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(trennzeichen_antworten, {"tag": 1033, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(benötigt_qualitätsprüfung, {"tag": 1034, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(leere_werte, {"tag": 1035, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(leere_zeilen, {"tag": 1036, "name": "hat", "cardinality": "0-1"})
    qualitätsprüfung.children.connect(leere_spalten, {"tag": 1037, "name": "hat", "cardinality": "0-1"})
    
    metadaten.children.connect(verknüpftes_item_id, {"tag": 1038, "name": "hat", "cardinality": "0-1"})
    
    patient.children.connect(teilnehmer, {"tag": 1039, "name": "ist", "cardinality": "n"})
    patient.children.connect(patient_idat, {"tag": 1040, "name": "hat", "cardinality": "1"})
    patient.children.connect(patient_id, {"tag": 1041, "name": "hat", "cardinality": "1"})
    
    antwortgruppe.children.connect(reihen_id, {"tag": 1042, "name": "hat", "cardinality": "1"})
    antwortgruppe.children.connect(antwort, {"tag": 1043, "name": "hat", "cardinality": "n"})
    
    # metadaten.children.connect(einheit, {"tag": 1044, "name": "hat", "cardinality": "0-1"})

    load_all_knowledge_node_classes()

    return [
        forschung, studie, teilnehmer, studieninformationen, startdatum, enddatum, studien_id, studienname, beschreibungstext, drks_id, studienzweck, 
        datenerhebung, fragebogen, fragebogen_id, fragebogen_name, antwortgruppe, reihen_id, spalten_id, qualitätsprüfung, datentyp, minimum, maximum, auswahlmöglichkeiten, 
        trennzeichen_auswahlmöglichkeiten, trennzeichen_antworten, benötigt_qualitätsprüfung, leere_werte, leere_zeilen, leere_spalten, item, metadaten, 
        leistungserbringer, antwort, feldname, verknüpftes_item_id, patient, patient_idat, patient_id
    ]