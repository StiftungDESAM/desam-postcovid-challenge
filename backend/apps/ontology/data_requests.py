from neomodel.sync_.core import db
from .models import OntologyNode, OntologyNodeTypes

from knowledge.models import load_all_knowledge_node_classes
from typing import List

def get_all_nodes(request) -> List[OntologyNode]:
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