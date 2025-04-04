import pytest
from .decorators import neo4j_test
from ..models import OntologyNode, OntologyNodeTypes, OntologyRelationship
from ..graph_migrations import LeafDeletionMigration

@neo4j_test
@pytest.mark.parametrize("tag", ["Feldname", "Antwort"])
def test_partial_delete(tag):
    migration = LeafDeletionMigration(tag)
    
    migration.apply()

    with pytest.raises(OntologyNode.DoesNotExist):
        OntologyNode.nodes.get(tag = tag)
