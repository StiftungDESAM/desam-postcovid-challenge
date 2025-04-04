import pytest
from .decorators import neo4j_test
from ..models import OntologyNode, OntologyNodeTypes, OntologyRelationship
from ..graph_migrations import AdditionMigration

@pytest.fixture
def addition():
    return AdditionMigration(
        new_node = OntologyNode(
            tag = "NewLeafNode",
            name = "New Leaf Node",
            node_type = OntologyNodeTypes.LEAF
        ),
        new_relationship = OntologyRelationship(
            tag = "2000",
            name = "HAT",
            cardinality = "n"
        ),
        parent_tag = "Metadaten"
    )

@neo4j_test
def test_creation(addition: AdditionMigration):
    addition.apply()

    nodes = OntologyNode.nodes.filter(tag = addition.new_node.tag)
    assert len(nodes) == 1

@neo4j_test
def test_linking(addition: AdditionMigration):
    addition.apply()
    
    new_node: OntologyNode = OntologyNode.nodes.get(tag = addition.new_node.tag)
    relationships = addition.parent.children.all_relationships(new_node)
    assert len(relationships) == 1
