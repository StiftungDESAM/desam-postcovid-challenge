import neomodel
from neomodel.sync_.core import db
from dataclasses import dataclass

class RelationshipNotFound(Exception):
    pass

@dataclass
class LinkedNodes:
    start_node: neomodel.StructuredNode
    end_node: neomodel.StructuredNode
    relationship: neomodel.StructuredRel

def get_linked_nodes(label: str|None = None, **properties) -> LinkedNodes:
    # To prevent Cypher injection, all labels and properties are passed to it as parameters.
    optional_label = ":$($label)" if label else ""
    properties_cypher = ', '.join('{0}: ${0}'.format(property) for property in properties)

    query = f"MATCH (n1)-[r{optional_label} {{ {properties_cypher} }}]->(n2) RETURN n1, n2, r"
    parameters = {
        "label": label,
        **properties
    }

    results,_ = db.cypher_query(query, parameters, resolve_objects = True)

    if results:
        columns = results[0]
        return LinkedNodes(
            start_node = columns[0],
            end_node = columns[1],
            relationship = columns[2]
        )
    raise RelationshipNotFound("Relationship matching query not found.")

def get_all_outgoing_relationships(node: neomodel.StructuredNode, label: str|None = None, **properties) -> list[LinkedNodes]:
    # To prevent Cypher injection, all labels and properties are passed to it as parameters.
    optional_label = ":$($label)" if label else ""
    properties_cypher = ', '.join('{0}: ${0}'.format(property) for property in properties)

    query = f"MATCH (n1)-[r{optional_label} {{ {properties_cypher} }}]->(n2) WHERE ELEMENTID(n1)=$node_id RETURN n1, n2, r"
    parameters = {
        "label": label,
        "node_id": node.element_id,
        **properties
    }

    results,_ = db.cypher_query(query, parameters, resolve_objects = True)

    return [
        LinkedNodes(
            start_node = row[0],
            end_node = row[1],
            relationship = row[2]
        )
        for row in results
    ]

def get_all_incoming_relationships(node: neomodel.StructuredNode, label: str|None = None, **properties) -> list[LinkedNodes]:
    # To prevent Cypher injection, all labels and properties are passed to it as parameters.
    optional_label = ":$($label)" if label else ""
    properties_cypher = ', '.join('{0}: ${0}'.format(property) for property in properties)

    query = f"MATCH (n1)-[r{optional_label} {{ {properties_cypher} }}]->(n2) WHERE ELEMENTID(n2)=$node_id RETURN n1, n2, r"
    parameters = {
        "label": label,
        "node_id": node.element_id,
        **properties
    }

    results,_ = db.cypher_query(query, parameters, resolve_objects = True)

    return [
        LinkedNodes(
            start_node = row[0],
            end_node = row[1],
            relationship = row[2]
        )
        for row in results
    ]
