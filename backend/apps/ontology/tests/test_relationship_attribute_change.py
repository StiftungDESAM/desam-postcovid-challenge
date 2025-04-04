import pytest
from ..graph_migrations import RelationshipAttributeChangeMigration
from ..models import OntologyNode, OntologyRelationship, OntologyNodeTypes
from ..utils import get_linked_nodes
from .decorators import neo4j_test

@neo4j_test
def test_renaming():
    relationship_tag = "1002"
    new_name = "SOMETHING_NEW"
    migration = RelationshipAttributeChangeMigration(relationship_tag, name = new_name)

    migration.apply()

    relationship: OntologyRelationship = get_linked_nodes(label = OntologyNode.get_relationship_label(), tag = relationship_tag).relationship
    assert relationship.name == new_name

@neo4j_test
def test_cardinality_change():
    relationship_tag = "1002"
    new_cardinality = "1"
    migration = RelationshipAttributeChangeMigration(relationship_tag, cardinality = new_cardinality)

    migration.apply()

    relationship: OntologyRelationship = get_linked_nodes(label = OntologyNode.get_relationship_label(), tag = relationship_tag).relationship
    assert relationship.cardinality == new_cardinality
