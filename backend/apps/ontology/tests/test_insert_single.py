import pytest
from .decorators import neo4j_test
from ..models import OntologyNode, OntologyNodeTypes, OntologyRelationship
from ..graph_migrations import InsertionSingleMigration

@neo4j_test
def test_insertion_single():
    migration = InsertionSingleMigration(
        relationship_tag = "1001",
        new_node = OntologyNode(
            tag = "Projekt",
            name = "Projekt",
            node_type = OntologyNodeTypes.CONNECTIVE
        ),
        new_relationship = OntologyRelationship(
            tag = "2000",
            name = "IS_CONNECTED",
            cardinality = "n"
        )
    )
    
    migration.apply()

    start_node: OntologyNode = OntologyNode.nodes.get(tag = migration.start_node.tag)
    new_node: OntologyNode = OntologyNode.nodes.get(tag = migration.new_node.tag)
    end_node: OntologyNode = OntologyNode.nodes.get(tag = migration.end_node.tag)
    
    rel1 = start_node.children.relationship(new_node)
    rel2 = new_node.children.relationship(end_node)
    assert rel1.tag == migration.new_relationship.tag
    assert rel2.tag == migration.relationship_tag

