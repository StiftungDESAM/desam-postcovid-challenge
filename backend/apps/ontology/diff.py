import rdflib
import io
from dataclasses import dataclass, field
from ontology.models import OntologyNode, OntologyRelationship, OntologyNodeTypes
from ontology.utils import get_relationship, get_all_relationships
from urllib.parse import quote
from rdflib.namespace import XSD
import logging
import re

 
UMLAUTS_MAPPING = str.maketrans({
    'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
    'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
    'ß': 'ss'
})

logger = logging.getLogger(__name__)
@dataclass
class Entity:
    """This is a utility class used for collecting the information on all entities in a graph from a RDF file
    Each line in an RDF file contains a triple which defines exactly one thing, e.g. a property of a node, a relationship, ...
    This means that all lines that relate to the same node/relationship ("entity" refers to both) must be combined.
    Then, in a later step, we can e.g. find the node entities that are linked together by a relationship.

    Entities should be initialized by load_entities(...) so that all connections are initialized correctly.
    """
    id: str|None = field(default = None)        # ID in the RDF file, must be set for export
    subject: str|None = field(default = None)   # The subject of the line defining the entity (e.g. node#3 or relationship#10)
    name: str = field(default = "")             # Name of the entity in the type definition triple
    properties: dict[str, str] = field(default_factory = dict)  # Dictionary containing all properties of an entity (e.g. tag, name, ...)

    # If the entity represents a node, this dictionary contains the ids of each outgoing relationship and the target node
    relationships: dict[str, str] = field(default_factory = dict) 

    # If the entity represents a relationship, the source is the start node and the target the end node.
    source: 'Entity' = field(default = None)
    target: 'Entity' = field(default = None)

    # The detected changes are written to this dictionary.
    diff: dict[str, str] = field(default_factory = dict)

    @property
    def is_node(self):
        return self.subject and self.subject.startswith("node#")
    
    @property
    def is_relationship(self):
        return self.subject and self.subject.startswith("relationship#")
    
    @classmethod
    def from_node(cls, node: OntologyNode):
        return cls(
            name = node.name,
            properties = {
                "tag": node.tag,
                "name": node.name,
                "is_leaf": node.node_type == OntologyNodeTypes.LEAF,
                "is_stakeholder": node.node_type == OntologyNodeTypes.STAKEHOLDER,
            }
        )
    
    @classmethod
    def from_relationship(cls, relationship: OntologyRelationship):
        return cls(
            name = relationship.name,
            properties = {
                "tag": relationship.tag,
                "name": relationship.name,
                "cardinality": relationship.cardinality
            }
        )
    
    def to_node_or_relationship(self) -> OntologyNode|OntologyRelationship:
        if self.is_node:
            # Gets node type from is_leaf/is_stakeholder properties
            if self.properties["is_leaf"]:
                node_type = OntologyNodeTypes.LEAF
            elif self.properties["is_stakeholder"]:
                node_type = OntologyNodeTypes.STAKEHOLDER
            else:
                node_type = OntologyNodeTypes.CONNECTIVE

            return OntologyNode(
                tag = self.properties["tag"],
                name = self.properties["name"],
                node_type = node_type
            )
        elif self.is_relationship:
            return OntologyRelationship(
                tag = self.properties["tag"],
                name = self.properties["name"],
                cardinality = self.properties["cardinality"]
            )
        else:
            raise ValueError("This entity is neither a node nor a relationship.")
    
    def __hash__(self):
        return hash((self.name))
    
    def __eq__(self, other):
        return self.name == other.name

def remove_prefix(text: str, delimiter: str = "/"):
    """Removes unnecessary trash from the RDF elements."""
    last_occurence = text.rfind(delimiter) + 1
    return text[last_occurence:]

def replace_umlauts(rdf):
    """ Replaces umlauts in the rdf string to allow parsing with rdf lib """

    processed_lines = []
    for line in rdf.splitlines():
        match = re.search(r'\s[a] pro:[a-zA-Z0-9]', line)
        if match:
            before = line[:match.start()]
            after = line[match.start():]
            after_translated = after.translate(UMLAUTS_MAPPING)
            processed_lines.append(before + after_translated)
        else:
            processed_lines.append(line)

    return '\n'.join(processed_lines)

def load_entities(rdf: str) -> dict[str, Entity]:
    """Loads the RDF file and gets all entities (nodes and relationships) from it.
    Automatically groups all triples belonging to an entity into one Entity instance.
    Returns a dictionary mapping entity tags to Entity instances."""
        
    graph = rdflib.Graph()
    graph.parse(io.StringIO(rdf))

    # Iterates over the RDF for the first time and combines all related entries into entities (like nodes or relationships).
    entities: dict[str, Entity] = {}
    for subject, predicate, obj in graph:

        # Removes unnecessary trash path at the front of all values.
        subject = remove_prefix(subject)
        predicate = remove_prefix(predicate)
        obj = remove_prefix(obj)
        
        # Creates a new entity if this is the first occurence of the subject.
        if subject not in entities:
            entity = Entity(subject = subject)
            entities[subject] = entity
        else:
            entity = entities[subject]

        # Saves the predicate&object into the entity depending on type.
        if predicate.startswith("property"):
            property_name = remove_prefix(predicate, "#")
            entity.properties[property_name] = obj
        if predicate.startswith("relationship"):
            # relationship_id = remove_prefix(predicate, "#")
            entity.relationships[predicate] = obj
        if predicate.startswith("22-rdf-syntax-ns"):
            name = remove_prefix(obj, "#")
            entity.name = name

    # Iterates over the entities a second time to resolve relationships.
    for i, entity in enumerate(entities.values()):
        entity.id = str(i)
        for relationship_name, node_name in entity.relationships.items():
            relationship = entities[relationship_name]
            target_node = entities[node_name]
            relationship.source = entity
            relationship.target = target_node

    return {
        entity.properties.get("tag"): entity
        for entity in entities.values()
    }

def annotate_new_and_modified_nodes(entities: dict[str, Entity]):
    """Annotates all nodes in the given entity list if they're new or have been modified."""
    for entity in entities.values():
        # This function only handles nodes, everything else is skipped.
        if not entity.is_node:
            continue

        try:
            tag = entity.properties.get("tag")
            node: OntologyNode = OntologyNode.nodes.get(tag = tag)

            # Collects the fields that have been changed.
            modified_fields = []
            # NOTE: created_at and updated_at are currently not tracked because they're just there for change tracking and not part of the ontology.
            if node.name != entity.properties.get("name"):
                modified_fields.append("name")

            node_is_stakeholder = (node.node_type == OntologyNodeTypes.STAKEHOLDER)
            entity_is_stakeholder = (entity.properties.get("is_stakeholder") == "true")
            if  node_is_stakeholder != entity_is_stakeholder:
                modified_fields.append("is_stakeholder")

            node_is_leaf = (node.node_type == OntologyNodeTypes.LEAF)
            entity_is_leaf = (entity.properties.get("is_leaf") == "true")
            logger.debug(f"node ist {node.name} and is leaf is {node_is_leaf}, entity is {entity.name} and entity is leaf {entity_is_leaf}")
            if node_is_leaf != entity_is_leaf:
                modified_fields.append("is_leaf")
            
            if modified_fields:
                logger.debug(f"modiefied fields are {modified_fields} for node {node.name}")
                entity.diff["modified"] = modified_fields
        except OntologyNode.DoesNotExist:
            # If an entity doesn't exist in the current ontology yet, the new ontology adds it.
            #logger.debug("new entity")
            entity.diff["added"] = True

def annotate_deleted_nodes(entities: dict[str, Entity]):
    """Checks if there are nodes in the ontology that are deleted in the new version.
    Extends the entity list with these and annotates them with the "deleted" tag."""
    # Collects all node tags in the new version.
    entity_tags = [tag for tag, entity in entities.items() if entity.is_node]
    entity_id = len(entities)

    # Finds all nodes that have been deleted and adds them to the entity list.
    for node in OntologyNode.nodes.all():
        if node.tag not in entity_tags:
            entity = Entity.from_node(node)
            entity.subject = "node#deleted" # necessary so that the entity is recognized as a node.
            entity.diff["deleted"] = True
            entity.id = str(entity_id)
            entity_id += 1
            entities[node.tag] = entity

def annotate_new_and_modified_relationships(entities: dict[str, Entity]):
    """Annotates all relationships in the given entity list if they're new or have been modified."""
    for tag, entity in entities.items():
        # This function only annotates relationships, everything else is skipped.
        if not entity.is_relationship:
            continue
        # Gets the relationship for the entity's tag.
        linked_nodes = get_relationship(label = OntologyNode.get_relationship_label(), tag = tag)

        if linked_nodes is None:
            # If the relationship doesn't exist in the current version of the ontology yet, the new ontology adds it.
            entity.diff["added"] = True
        else:
            # Collects all properties that have been modified.
            relationship: OntologyRelationship = linked_nodes.relationship
            modified_fields = []
            
            if relationship.name != entity.properties.get("name"):
                modified_fields.append("name")

            if relationship.cardinality != entity.properties.get("cardinality"):
                modified_fields.append("cardinality")

            if modified_fields:
                entity.diff["modified"] = modified_fields

def annotate_deleted_relationships(entities: dict[str, Entity]):
    """Checks for relationships that don't exist anymore in the new ontology.
    In this case, they're added to the entity list and annotated as deleted."""
    entity_tags = [tag for tag, entity in entities.items() if entity.is_relationship]
    all_relationships = get_all_relationships(label = OntologyNode.get_relationship_label())
    entity_id = len(entities)

    for linked_nodes in all_relationships:
        relationship: OntologyRelationship = linked_nodes.relationship
        if relationship.tag not in entity_tags:
            entity = Entity.from_relationship(relationship)
            entity.diff["deleted"] = True
            entity.subject = "relationship#deleted" # necessary so that the entity is recognized as a relationship.
            entity.id = str(entity_id)

            # TODO: Somehow handle the case the nodes and relationships have the same tag.
            # We currently use numbers as relationship tags and strings as node tags, so I'll just leave this be for now.
            entity.source = entities[linked_nodes.start_node.tag]
            entity.target = entities[linked_nodes.end_node.tag]
            entities[relationship.tag] = entity
            entity_id += 1

def annotate_relinked_relationships(entities: dict[str, Entity]):
    for tag, entity in entities.items():
        if not entity.is_relationship:
            continue

        existing_link = get_relationship(label = OntologyNode.get_relationship_label(), tag = tag)

        # The link has been deleted.
        if existing_link is None:
            logger.debug("relationship not existing")
            continue
        
        new_source_tag = entity.source.properties.get("tag")
        if new_source_tag != existing_link.start_node.tag and "modified" not in entity.diff:
            entity.diff["modified"] = []

        new_target_tag = entity.target.properties.get("tag")
        if new_target_tag != existing_link.end_node.tag and "modified" not in entity.diff:
            entity.diff["modified"] = []

#not pretty but we need to adress the datatypes
def add_property_types(name, graph, entity,NOD,PRO,value):
    if(name=="created" or name=="last_updated"):
        graph.add((NOD[entity.id], PRO[name], rdflib.Literal(value, datatype=XSD.dateTime)))
    elif(name=="is_stakeholder" or name=="verified" or name=="is_leaf" or name=="added"
         or name=="deleted"):
        graph.add((NOD[entity.id], PRO[name], rdflib.Literal(value, datatype=XSD.boolean)))
    else:
        graph.add((NOD[entity.id], PRO[name], rdflib.Literal(value)))


def add_relation_property_types(name, graph, entity,REL,PRO,value):
    if(name=="created" or name=="last_updated"):
        graph.add((REL[entity.id], PRO[name], rdflib.Literal(value, datatype=XSD.dateTime)))
    elif(name=="is_stakeholder" or name=="verified" or name=="is_leaf" or name=="added"
         or name=="deleted"):
        graph.add((REL[entity.id], PRO[name], rdflib.Literal(value, datatype=XSD.boolean)))
    #elif(name=="tag"):
    #    graph.add((REL[entity.id], PRO[name], rdflib.Literal(value, datatype=XSD.long)))
    else:
        graph.add((REL[entity.id], PRO[name], rdflib.Literal(value)))


def serialize_with_explicit_booleans(graph) -> str:
    # 1. Turtle-Output erzeugen
    turtle = graph.serialize(format="turtle", encoding="utf-8").decode("utf-8")

    # 2. Stelle sicher, dass Prefix xsd vorhanden ist (wenn nicht, ergänzen)
    if "xsd:" not in turtle:
        turtle = '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n' + turtle

    # 3. Regex-Ersetzungen: nackt `true` und `false` → explizite typed literals
    
    turtle = re.sub(r'(?<=\s)(true|false)(?=\s*[;.\)])', r'"\1"^^xsd:boolean', turtle)

    return turtle

def entities_to_rdf(entities: list[Entity]) -> str:
    """Serializes the entities into an RDF string in TURTLE format."""
    graph = rdflib.Graph()

    # Namespace definitions
    RDF = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    PRO = rdflib.Namespace("property#")
    NOD = rdflib.Namespace("node#")
    REL = rdflib.Namespace("relationship#")


    # Bindings of namespaces
    graph.bind("rdf", RDF, replace=True)
    graph.bind("xsd", XSD ,replace=True)
    graph.bind("pro", PRO, replace=True)
    graph.bind("nod", NOD, replace=True)
    graph.bind("rel", REL, replace=True)


    # Adding the entities to the RDF graph
    for entity in entities:
        tag = entity.properties.get("tag")
        if entity.is_node:
            graph.add((NOD[entity.id], RDF.type, PRO[tag]))
            
            # Definition of all node properties
            for property_name, property_value in entity.properties.items():
                property_name = quote(property_name)
                add_property_types(property_name,graph,entity,NOD,PRO,property_value)
                #missing datetypes
                #graph.add((NOD[entity.id], PRO[property_name], rdflib.Literal(property_value)))
            if entity.diff:
                for name,value in entity.diff.items():
                    name = quote(name)
                    graph.add((NOD[entity.id], PRO[name], rdflib.Literal("true", datatype=XSD.boolean))) 

        elif entity.is_relationship:
            graph.add((REL[entity.id], RDF.type, PRO[tag]))
            graph.add((NOD[entity.source.id], REL[entity.id], NOD[entity.target.id]))
            
            # Defintion of all relationship properties
            for property_name, property_value in entity.properties.items():
                property_name = quote(property_name)
                add_relation_property_types(property_name,graph,entity,REL,PRO,property_value)
                #graph.add((REL[entity.id], PRO[property_name], rdflib.Literal(property_value)))
            if entity.diff:
                for name,value in entity.diff.items():
                    name = quote(name)
                    if(name == "modified" and value):
                        
                        #logger.debug(f"found modified bla {value}")
                        graph.add((REL[entity.id], PRO[name], rdflib.Literal(value)))
                    elif(name == "modified" and not value):
                        logger.debug("relationship doesnt has diff")
                    else:
                        o=rdflib.Literal("true", datatype=XSD.boolean)
                        graph.add((REL[entity.id], PRO[name], o))

    #text = graph.serialize(format="turtle", encoding="utf-8").decode("utf-8")
    
    #RDF must contain english carachters. It doesnt work with german umlaute because utf8 encoding is only possible for the values, not the names.
    return serialize_with_explicit_booleans(graph)


def from_rdf(new_rdf: str) -> str:
    """Takes an RDf file as string and returns an RDF file with the diff included."""
    rdf = replace_umlauts(new_rdf)
    entities = load_entities(rdf)

    annotate_new_and_modified_nodes(entities)
    annotate_new_and_modified_relationships(entities)
    annotate_relinked_relationships(entities)
    annotate_deleted_nodes(entities)
    annotate_deleted_relationships(entities)

    return entities_to_rdf(entities.values())
    
def ontology_export_rdf(entities):

    
    return entities_to_rdf(entities)

