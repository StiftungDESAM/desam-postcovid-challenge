import pytest
from ..operations import UnlinkingMigration
from ontology.models import OntologyNode
from ontology.utils import get_linked_nodes, RelationshipNotFound
from .decorators import neo4j_test

@pytest.fixture
def unlinking():
    return UnlinkingMigration(tag = "1008")

@neo4j_test
def test_unlinking(unlinking: UnlinkingMigration):
    unlinking.apply()

    with pytest.raises(RelationshipNotFound):
        get_linked_nodes(label = OntologyNode.get_relationship_label(), tag = unlinking.tag)
