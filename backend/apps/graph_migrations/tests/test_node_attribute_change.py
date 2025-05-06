import pytest
from ..operations import NodeAttributeChangeMigration
from ontology.models import OntologyNode, OntologyNodeTypes
from .decorators import neo4j_test

@neo4j_test
def test_renaming():
    node_tag = "Item"
    new_name = "Changed Name"
    migration = NodeAttributeChangeMigration(node_tag, node_name = new_name)

    migration.apply()

    node: OntologyNode = OntologyNode.nodes.get(tag = node_tag)
    assert node.name == new_name
