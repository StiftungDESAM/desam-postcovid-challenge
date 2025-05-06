from neomodel.sync_.core import db
from .diff import load_entities
from .models import OntologyNode, OntologyRelationship

def import_rdf(rdf: str):
    entities = load_entities(rdf)

    # Step 1: Clear ontology graph
    db.cypher_query("MATCH (n:OntologyNode) DETACH DELETE n")

    # Step 2: Import ontology nodes
    nodes: dict[str, OntologyNode] = dict()
    for tag, entity in entities.items():
        if not entity.is_node or "deleted" in entity.properties:
            continue

        node: OntologyNode = entity.to_node_or_relationship()
        node.save()
        nodes[tag] = node

    # Step 3: Connect ontology nodes
    for tag, entity in entities.items():
        if not entity.is_relationship or "deleted" in entity.properties:
            continue

        relationship: OntologyRelationship = entity.to_node_or_relationship()
        source_tag = entity.source.properties["tag"]
        target_tag = entity.target.properties["tag"]
        nodes[source_tag].children.connect(nodes[target_tag], relationship.properties)