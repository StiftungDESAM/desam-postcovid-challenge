from neomodel.sync_.core import db
import functools

def neo4j_test(func):
    """Runs a function inside a Neo4j transaction and rolls back afterwards."""
    @functools.wraps(func)
    def run_and_roll_back(*args, **kwargs):
        db.begin()
        try:
            return func(*args, **kwargs)
        finally:
            db.rollback()
    return run_and_roll_back