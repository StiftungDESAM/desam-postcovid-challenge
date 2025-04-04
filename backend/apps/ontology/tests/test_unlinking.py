import pytest
from ..graph_migrations import UnlinkingMigration
from ..models import OntologyNode
from ..utils import get_linked_nodes, LinkedNodes, RelationshipNotFound
from .decorators import neo4j_test

@pytest.fixture
def unlinking():
    return UnlinkingMigration(tag = "1008")

@neo4j_test
def test_unlinking(unlinking: UnlinkingMigration):
    unlinking.apply()

    with pytest.raises(RelationshipNotFound):
        get_linked_nodes(label = OntologyNode.get_relationship_label(), tag = unlinking.tag)
