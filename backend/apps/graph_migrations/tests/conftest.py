import pytest
import os
from ontology.data_requests import create_example_ontology

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
    create_example_ontology()
