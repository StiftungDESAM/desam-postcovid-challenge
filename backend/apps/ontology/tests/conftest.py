import pytest
import os

@pytest.hookimpl(tryfirst=True)
def pytest_configure():
    if not os.getenv("ENABLE_UNIT_TESTS"):
        pytest.exit("ERROR: Unit tests are disabled. Please make sure that you're not trying to run unit tests on a production system!\n" \
                    "You can enable unit tests by setting ENABLE_UNIT_TESTS=1.", returncode=1)

@pytest.fixture(autouse = True, scope = "session")
def setup_database():
    """This fixture is called exactly once at the beginning of the test session."""
    from neomodel.sync_.core import db
    db.cypher_query("MATCH (n) DETACH DELETE n")
    # NOTE: At a later point, the database can be filled with dummy data here instead.
    create_dummy_data()

def create_dummy_data():
    from ..models import OntologyNode, OntologyRelationship, OntologyNodeTypes
    forschung: OntologyNode = OntologyNode(tag="Forschung", name="Forschung", node_type=OntologyNodeTypes.STAKEHOLDER).save()
    studie: OntologyNode = OntologyNode(tag="Studie", name="Studie", node_type=OntologyNodeTypes.CONNECTIVE).save()
    teilnehmer: OntologyNode = OntologyNode(tag="Teilnehmer", name="Teilnehmer", node_type=OntologyNodeTypes.CONNECTIVE).save()
    datenerhebung: OntologyNode = OntologyNode(tag="Datenerhebung", name="Datenerhebung", node_type=OntologyNodeTypes.CONNECTIVE).save()
    fragebogen: OntologyNode = OntologyNode(tag="Fragebogen", name="Fragebogen", node_type=OntologyNodeTypes.CONNECTIVE).save()
    item: OntologyNode = OntologyNode(tag="Item", name="Item", node_type=OntologyNodeTypes.CONNECTIVE).save()
    metadaten: OntologyNode = OntologyNode(tag="Metadaten", name="Metadaten", node_type=OntologyNodeTypes.CONNECTIVE).save()
    leistungserbringer: OntologyNode = OntologyNode(tag="Leistungserbringer", name="Leistungserbringer", node_type=OntologyNodeTypes.STAKEHOLDER).save()
    antwort: OntologyNode = OntologyNode(tag="Antwort", name="Antwort", node_type=OntologyNodeTypes.LEAF).save()
    feldtyp: OntologyNode = OntologyNode(tag="Feldtyp", name="Feldtyp", node_type=OntologyNodeTypes.LEAF).save()
    benötigt: OntologyNode = OntologyNode(tag="Benötigt", name="Benötigt", node_type=OntologyNodeTypes.LEAF).save()
    frage: OntologyNode = OntologyNode(tag="Frage", name="Frage", node_type=OntologyNodeTypes.LEAF).save()
    feldname: OntologyNode = OntologyNode(tag="Feldname", name="Feldname", node_type=OntologyNodeTypes.LEAF).save()
    sektionsüberschrift: OntologyNode = OntologyNode(tag="Sektionsüberschrift", name="Sektionsüberschrift", node_type=OntologyNodeTypes.LEAF).save()
    mapping: OntologyNode = OntologyNode(tag="Mapping", name="Mapping", node_type=OntologyNodeTypes.LEAF).save()

    forschung.children.connect(studie, {"tag": 1001, "name": "erstellt", "cardinality": "n"})
    studie.children.connect(teilnehmer, {"tag": 1002, "name": "hat", "cardinality": "n"})
    leistungserbringer.children.connect(teilnehmer, {"tag": 1003, "name": "ist", "cardinality": "n"})
    teilnehmer.children.connect(antwort, {"tag": 1004, "name": "gibt", "cardinality": "n"})
    studie.children.connect(datenerhebung, {"tag": 1005, "name": "hat", "cardinality": "n"})
    datenerhebung.children.connect(fragebogen, {"tag": 1006, "name": "hat", "cardinality": "n"})
    fragebogen.children.connect(item, {"tag": 1007, "name": "hat", "cardinality": "n"})
    item.children.connect(antwort, {"tag": 1008, "name": "hat", "cardinality": "n"})
    item.children.connect(metadaten, {"tag": 1009, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(feldtyp, {"tag": 1010, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(benötigt, {"tag": 1011, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(frage, {"tag": 1012, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(feldname, {"tag": 1013, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(sektionsüberschrift, {"tag": 1014, "name": "hat", "cardinality": "n"})
    metadaten.children.connect(mapping, {"tag": 1015, "name": "hat", "cardinality": "n"})