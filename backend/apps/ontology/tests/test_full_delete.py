import pytest
from .decorators import neo4j_test
from ..models import OntologyNode, OntologyNodeTypes, OntologyRelationship
from ..graph_migrations import FullDeletionMigration

@neo4j_test
@pytest.mark.parametrize("tag", ["Metadaten", "Feldname", "Forschung"])
def test_partial_delete(tag):
    migration = FullDeletionMigration(tag)
    migration.validate()
    child_tags = [child.tag for child in migration.node.children.all()]
    
    migration.apply()

    remaining_nodes = OntologyNode.nodes.filter(tag__in = child_tags)
    assert len(remaining_nodes) == 0
