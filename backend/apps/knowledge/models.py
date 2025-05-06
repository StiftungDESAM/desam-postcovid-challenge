import neomodel
from neomodel import db

from django.utils import timezone
from ontology.models import OntologyNode, OntologyNodeTypes
from ontology.utils import get_all_outgoing_relationships
from typing import List, Type
import sys

class KnowledgeNode(neomodel.StructuredNode):
    # The tag property is added dynamically during the creation of knowledge node classes.
    # This allows us to pre-fill it with a default value so that we don't have to specify the tag for every knowledge node we create.
    # tag = neomodel.StringProperty(default = ...)
    uuid = neomodel.UniqueIdProperty()
    graph_id = neomodel.IntegerProperty(default=0)
    is_verified = neomodel.BooleanProperty(default = False)
    created_at = neomodel.DateTimeProperty(default = timezone.now)
    updated_at = neomodel.DateTimeProperty(default = timezone.now)

class KnowledgeRelationship(neomodel.StructuredRel):
    graph_id = neomodel.IntegerProperty(default=0)
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

class DataRelationship(neomodel.StructuredRel):
    graph_id = neomodel.IntegerProperty(default=0)

class LeafNode(KnowledgeNode):
    # Only leaf nodes can have connection to data nodes. There are three categories of data:
    current_data = neomodel.RelationshipTo("DataNode", "CURRENT", cardinality = neomodel.ZeroOrOne, model = DataRelationship)
    previous_data = neomodel.RelationshipTo("DataNode", "PREVIOUS", model = DataRelationship)
    # NOTE: Report specifies cardinality for in_review as 0-1, but can't multiple data requests be in review at the same time?
    in_review = neomodel.RelationshipTo("DataNode", "IN_REVIEW", model = DataRelationship)

class DataNode(neomodel.StructuredNode):
    uuid = neomodel.UniqueIdProperty()
    graph_id = neomodel.IntegerProperty(default=0)
    value = neomodel.StringProperty(max_length = 256*256)
    created_at = neomodel.DateTimeProperty(default = timezone.now)
    updated_at = neomodel.DateTimeProperty(default = timezone.now)

def load_knowledge_node_class(ontology_node: OntologyNode, force_reload: bool = False) -> Type[neomodel.StructuredNode]:
    """
    Dynamically creates a StructuredNode sub-class for a specific ontology node.
    E.g. if there's an ontology node with the tag "Patient", this would create a "Patient" class.
    This allows us to use this class as a label in the knowledge graph.
    If force_reload is True, any existing entry of this ontology node in the neomodel NODE_CLASS_REGISTRY is overwritten.
    This is required if you want to push a new version of an ontology node that must replace the old one.
    """

    if force_reload:
        # Removes all entries for this ontology node from the node class registry.
        ExistingNodeClass = ontology_node.node_class
        if ExistingNodeClass is not None:
            entries_to_delete = [labels for labels, node_class in db._NODE_CLASS_REGISTRY.items() if node_class==ExistingNodeClass]
            for entry in entries_to_delete:
                del db._NODE_CLASS_REGISTRY[entry]
    
    # This dictionary contains all fields and methods of the knowledge node class to be created.
    class_fields = {
        # Without specifying the module explicitly, neomodel thinks the class comes from neomodel.sync_.core which leads to import errors.
        "__module__": "knowledge.models",
        
        # The tag property is added dynamically so that the default can be set based on the ontology node.
        "tag": neomodel.StringProperty(default = ontology_node.tag),
        
        # NOTE: Test to get name from ontology node into knowledge nodes.
        #"name": neomodel.StringProperty(default = ontology_node.name)
    }

    # This query gets all relationships of the ontology node.
    links = get_all_outgoing_relationships(ontology_node, label = OntologyNode.get_relationship_label())

    # Creates the relationship manager for each found relationship and adds it to the class definition.
    for linked_nodes in links:
        relationship = linked_nodes.relationship
        other_node = linked_nodes.end_node

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

def load_all_knowledge_node_classes(force_reload = False) -> List[Type[neomodel.StructuredNode]]:
    """
    Loads the knowledge node classes for all ontology nodes in the graph database.
    If a knowledge node class doesn't exist yet, it's created. Otherwise, it's loaded from the node registry.
    If force_reload is True, all classes are re-created and existing entries in the node registry overwritten.
    """
    ontology_nodes = list(OntologyNode.nodes.all())

    for ontology_node in ontology_nodes:
        if force_reload:
            KnowledgeNodeClass = load_knowledge_node_class(ontology_node, force_reload=True)
        else:
            KnowledgeNodeClass = ontology_node.node_class

        if KnowledgeNodeClass is None:
            raise ImportError(f"Knowledge node class '{ontology_node.tag}' couldn't be loaded or created.")
        # KnowledgeNodeClass = create_knowledge_node_class(ontology_node)

        # The dynamically added classes must be added to this module explicitly so that neomodel can find them.
        setattr(sys.modules[__name__], KnowledgeNodeClass.__name__, KnowledgeNodeClass)

# Only loads classes when the server is started and not e.g. during migrations.
# This would cause errors because load_all_knowledge_node_classes attempts to access the Neoj4 database.
if sys.argv[1] == "runserver" or "gunicorn" in sys.argv[0]:
    load_all_knowledge_node_classes()