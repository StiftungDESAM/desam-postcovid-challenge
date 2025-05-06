import pytest
from .decorators import neo4j_test
from ontology.models import OntologyNode, OntologyNodeTypes, OntologyRelationship
from ..operations import PartialDeletionMigration

@neo4j_test
@pytest.mark.parametrize("tag", ["Fragebogen", "Item", "Teilnehmer"])
def test_partial_delete(tag):
    migration = PartialDeletionMigration(tag)
    migration.validate()

    parents: list[OntologyNode] = migration.target.parents.all()
    children: list[OntologyNode] = migration.target.children.all()
    
    migration.apply()

    if parents:
        all_children = set(parents[0].children.all())
        assert set(children).issubset(all_children)
    if children:
        all_parents = set(children[0].parents.all())
        assert set(parents).issubset(all_parents)

    with pytest.raises(OntologyNode.DoesNotExist):
        OntologyNode.nodes.get(tag = migration.target.tag)

    

