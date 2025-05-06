import pytest
from .decorators import neo4j_test
from ontology.models import OntologyNode, OntologyNodeTypes, OntologyRelationship
from ..operations import InsertionMultipleMigration

@neo4j_test
def test_insertion_multiple():
    migration = InsertionMultipleMigration(
        new_node = OntologyNode(
            tag = "InbetweenNode",
            name = "Inbetween Node",
            node_type = OntologyNodeTypes.CONNECTIVE
        ),
        new_relationship = OntologyRelationship(
            tag = "2000",
            name = "IS_CONNECTED",
            cardinality = "n"
        ),
        relationship_tags = ["1010", "1011", "1012"]
    )
    migration.validate()
    children_before_migration = len(migration.start_node.children.all())
    expected_children_after_migration = children_before_migration - len(migration.relationship_tags) + 1
    
    migration.apply()

    start_node: OntologyNode = OntologyNode.nodes.get(tag = migration.start_node.tag)
    new_node: OntologyNode = OntologyNode.nodes.get(tag = migration.new_node.tag)

    # It's expected that the start node lost the re-linked children, and gained the new connective node.
    assert len(new_node.children.all()) == len(migration.relationship_tags)
    assert len(start_node.children.all()) == expected_children_after_migration

