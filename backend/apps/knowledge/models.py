import neomodel
from neomodel.sync_.core import db

from django.utils import timezone
import neomodel.sync_
from ontology.models import OntologyNode, OntologyNodeTypes
from typing import List, Type
import sys

class KnowledgeNode(neomodel.StructuredNode):
    # The tag property is added dynamically during the creation of knowledge node classes.
    # This allows us to pre-fill it with a default value so that we don't have to specify the tag for every knowledge node we create.
    # tag = neomodel.StringProperty(default = ...)
    is_verified = neomodel.BooleanProperty(default = False)
    created_at = neomodel.DateTimeProperty(default = timezone.now)
    updated_at = neomodel.DateTimeProperty(default = timezone.now)

class KnowledgeRelationship(neomodel.StructuredRel):
    is_verified = neomodel.BooleanProperty(default = False)
    created_at = neomodel.DateTimeProperty(default = timezone.now)
    updated_at = neomodel.DateTimeProperty(default = timezone.now)

# These are the three possible knowledge node base classes.
# They're all abstract and are just used as base classes for node classes generated dynamically by create_knowledge_node_class.
# The relationships between them are therefore also defined dynamically by create_knowledge_node_class.
class StakeholderNode(KnowledgeNode):
    # This field uniquely identifies a stakeholder for record linkage.
    # NOTE: The uniqueness is currently not enforced using a database constraint. 
    # NOTE: stakeholder_id and tag must be unique in combination, this is currently impossible with neomodel.
    stakeholder_id = neomodel.StringProperty(max_length = 256)

class ConnectiveNode(KnowledgeNode):
    pass

class LeafNode(KnowledgeNode):
    # Only leaf nodes can have connection to data nodes. There are three categories of data:
    current_data = neomodel.RelationshipTo("DataNode", "CURRENT", cardinality = neomodel.ZeroOrOne)
    previous_data = neomodel.RelationshipTo("DataNode", "PREVIOUS")
    # NOTE: Report specifies cardinality for in_review as 0-1, but can't multiple data requests be in review at the same time?
    in_review = neomodel.RelationshipTo("DataNode", "IN_REVIEW")

class DataNode(neomodel.StructuredNode):
    value = neomodel.StringProperty(max_length = 256*256)
    created_at = neomodel.DateTimeProperty(default = timezone.now)
    updated_at = neomodel.DateTimeProperty(default = timezone.now)

def load_knowledge_node_class(ontology_node: OntologyNode) -> Type[neomodel.StructuredNode]:
    """
    Dynamically creates a StructuredNode sub-class for a specific ontology node.
    E.g. if there's an ontology node with the tag "Patient", this would create a "Patient" class.
    This allows us to use this class as a label in the knowledge graph.
    """
    
    # This dictionary contains all fields and methods of the knowledge node class to be created.
    class_fields = {
        # Without specifying the module explicitly, neomodel thinks the class comes from neomodel.sync_.core which leads to import errors.
        "__module__": "knowledge.models",
        
        # The tag property is added dynamically so that the default can be set based on the ontology node.
        "tag": neomodel.StringProperty(default = ontology_node.tag)
    }

    # This query gets all relationships of the ontology node.
    # ! node_label and relation_label are NOT sanitized against CYPHER injection!
    # ! Because they're labels, they cannot be passed as parameters to the query which would make them safe.
    # ! As they're unsafe, we must ensure that ontology node and relationship labels are properly sanitized when they're set.
    get_relationships_query = """
        MATCH (n1:{node_label}{{tag: $node_tag}})-[r:{relation_label}]->(n2:{node_label})
        RETURN r, n2
    """.format(
        node_label = OntologyNode.__label__, 
        relation_label = OntologyNode.get_relationship_label()
    )
    results,_ = db.cypher_query(get_relationships_query, {"node_tag": ontology_node.tag}, resolve_objects = True)

    # Creates the relationship manager for each found relationship and adds it to the class definition.
    for relationship, other_node in results:
        # NOTE: Cardinality would be implemented here by setting the cardinality parameter of the relationship manager.
        relationship_manager = neomodel.RelationshipTo("knowledge.models." + other_node.tag, relationship.name, model = KnowledgeRelationship)
        relationship_name = f"{relationship.name}_{other_node.tag}".lower()
        class_fields[relationship_name] = relationship_manager

    # Dynamically creates the class.
    class_name = ontology_node.tag

    match ontology_node.node_type:
        case OntologyNodeTypes.LEAF:
            base_class = LeafNode
        case OntologyNodeTypes.CONNECTIVE:
            base_class = ConnectiveNode
        case OntologyNodeTypes.STAKEHOLDER:
            base_class = StakeholderNode
        case _:
            raise ValueError(f"Unknown ontology node type: '{ontology_node.node_type}'")

    return type(class_name, (base_class,), class_fields)

def load_all_knowledge_node_classes() -> List[Type[neomodel.StructuredNode]]:
    """
    Loads the knowledge node classes for all ontology nodes in the graph database.
    If a knowledge node class doesn't exist yet, it's created. Otherwise, it's loaded from the node registry.
    """
    for ontology_node in OntologyNode.nodes.all():
        KnowledgeNodeClass = ontology_node.node_class

        if KnowledgeNodeClass is None:
            raise ImportError(f"Knowledge node class '{ontology_node.tag}' couldn't be loaded or created.")
        # KnowledgeNodeClass = create_knowledge_node_class(ontology_node)

        # The dynamically added classes must be added to this module explicitly so that neomodel can find them.
        setattr(sys.modules[__name__], KnowledgeNodeClass.__name__, KnowledgeNodeClass)
