import pytest
from ..graph_migrations import NodeAttributeChangeMigration
from ..models import OntologyNode, OntologyNodeTypes
from .decorators import neo4j_test

@neo4j_test
def test_renaming():
    node_tag = "Item"
    new_name = "Changed Name"
    migration = NodeAttributeChangeMigration(node_tag, name = new_name)

    migration.apply()

    node: OntologyNode = OntologyNode.nodes.get(tag = node_tag)
    assert node.name == new_name
