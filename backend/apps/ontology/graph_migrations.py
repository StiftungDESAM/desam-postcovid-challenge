"""
This file contains the definition of all migration operations. These are outlined in the stage 2 report.
"""
import abc
import enum
from dataclasses import dataclass
from neomodel.sync_.core import db
from neomodel.sync_.match import NodeSet
from .models import OntologyNode, OntologyNodeTypes, OntologyRelationship
from .utils import get_linked_nodes, LinkedNodes, RelationshipNotFound, get_all_incoming_relationships, get_all_outgoing_relationships

class OntologyMigration(abc.ABC):
    @abc.abstractmethod
    def apply_to_ontology(self) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def apply_to_knowledge_graph(self) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def validate(self) -> None:
        """Checks if the migration is valid and raises an OntologyMigrationError if not."""
        raise NotImplementedError
    
    def apply(self):
        self.validate()
        self.apply_to_ontology()
        self.apply_to_knowledge_graph()
    
    @property
    def steps(self) -> list['OntologyMigrationStep']:
        """Returns the list of sub-steps this migration consists of. By default, this returns only one step, provided the self.target field is set."""
        return [OntologyMigrationStep(migration = self, target = self.target)]

    @property
    @abc.abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    ### VALIDATION HELPERS
    def _validate_that_node_exists(self, tag: str) -> OntologyNode:
        """Tries to get the node with the given tag and raises an OntologyMigrationError if it doesn't exist."""
        try:
            return OntologyNode.nodes.get(tag = tag)
        except OntologyNode.DoesNotExist as exc:
            raise OntologyMigrationError(self, f"Ontology node tag '{tag}' doesn't exist.")

    def _validate_that_relationship_exists(self, tag: str) -> LinkedNodes:
        """Tries to get the relationship with the given tag and raises an OntologyMigrationError if it doesn't exist."""
        try:
            return get_linked_nodes(label = OntologyNode.get_relationship_label(), tag = tag)
        except RelationshipNotFound as exc:
            raise OntologyMigrationError(self, f"Relationship tag '{tag}' doesn't exist.") from exc

    def _validate_that_node_doesnt_exist(self, tag: str) -> None:
        """Raises an OntologyMigrationError if a node with the given tag already exists."""
        if OntologyNode.nodes.filter(tag = tag):
            raise OntologyMigrationError(self, f"Ontology tag '{tag}' already exists")

    def _validate_that_relationship_doesnt_exist(self, tag: str) -> None:
        """Raises an OntologyMigrationError if a relationship with the given tag already exists."""
        try:
            get_linked_nodes(label = OntologyNode.get_relationship_label(), tag = tag)
            raise OntologyMigrationError(self, f"Relationship tag '{tag}' already exists.")
        except RelationshipNotFound:
            pass # Relationship doesn't exist yet, everything is ok

class OntologyMigrationError(Exception):
    def __init__(self, migration: OntologyMigration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.migration = migration

@dataclass
class OntologyMigrationStep:
    migration: "OntologyMigration"
    title: str
    target: OntologyNode | OntologyRelationship

class UnlinkingMigration(OntologyMigration):
    title = "UNLINKING"
    # TODO/Question: Doesn't an unlinking also always imply data loss, as a sub-graph in the knowledge graph will be unlinked?

    """Removes link between two ontology nodes."""
    def __init__(self, tag: str):
        self.tag = tag

    def validate(self):
        try:
            linked_nodes = get_linked_nodes(label = "IS_RELATED_TO", tag = self.tag)
        except RelationshipNotFound as exc:
            raise OntologyMigrationError(self, f"Relationship tag '{self.tag}' doesn't exist.") from exc

        self.start_node: OntologyNode = linked_nodes.start_node
        self.end_node: OntologyNode = linked_nodes.end_node
        self.target: OntologyNode = linked_nodes.relationship

        # A leaf node can only be unlinked, if it's linked to another parent node.
        if self.end_node.node_type == OntologyNodeTypes.LEAF and not self.end_node.parents.all():
            raise OntologyMigrationError(self, "Cannot unlink leaf nodes.")
        
        # TODO: For other node types we theoretically would have to verify, that no disconnected portion of the graph is created. 
        # This is omitted for now.

    def apply_to_ontology(self):
        self.start_node.children.disconnect(self.end_node)

    def apply_to_knowledge_graph(self):
        query = "MATCH (n1:$($start_label))-[r:$($relationship_label)]->(n2:$($end_label)) DELETE r"
        db.cypher_query(query, {
            "start_label": self.start_node.tag,
            "relationship_label": self.target.name,
            "end_label": self.end_node.tag
        })

class NodeAttributeChangeMigration(OntologyMigration):
    title = "ATTRIBUTE_MODIFICATION"
    # NOTE: Currently, changing of node type is not permitted.

    """If name is omitted, it doesn't change."""
    def __init__(self, tag: str, name: str|None = None):
        self.tag = tag
        self.name = name

    def validate(self):
        self.target = self._validate_that_node_exists(self.tag)

    def apply_to_ontology(self):
        if self.name is not None:
            self.target.name = self.name
        self.target.save()

    def apply_to_knowledge_graph(self):
        # Currently no attributes affecting the knowledge graph can be changed.
        pass

# NOTE: What happens when the cardinality changes and there are too many relationships in the knowledge graph?
class RelationshipAttributeChangeMigration(OntologyMigration):
    title = "ATTRIBUTE_MODIFICATION"

    """If name or cardinality is None or omitted, it doesn't change."""
    def __init__(self, tag: str, name: str|None = None, cardinality: str|None = None):
        # TODO: This should only take the relationship tag and changed attributes as parameters.
        self.tag = tag
        self.name = name
        self.cardinality = cardinality

    def validate(self):
        self.target: OntologyRelationship = self._validate_that_relationship_exists(self.tag).relationship
        # TODO: Should we validate if a cardinality change is incompatible with the knowledge graph here?

    def apply_to_ontology(self):
        if self.name is not None:
            self.target.name = self.name
        if self.cardinality is not None:
            self.target.cardinality = self.cardinality
        self.target.save()
    
    def apply_to_knowledge_graph(self):
        # NOTE: Currently, cardinality changes don't affect the knowledge graph.
        pass

class AdditionMigration(OntologyMigration):
    title = "ADDITION"

    # TODO: Switch the order of constructor parameters because the convention for other migrations is to start with the affected node/relationship, in this case the parent.
    """Creates and links a new ontology node."""
    def __init__(self, new_node: OntologyNode, new_relationship: OntologyRelationship, parent_tag: str):
        self.new_node = new_node
        self.new_relationship = new_relationship
        self.parent_tag = parent_tag

    def validate(self):
        self._validate_that_node_doesnt_exist(self.new_node.tag)
        self._validate_that_relationship_doesnt_exist(self.new_relationship.tag)
        self.parent = self._validate_that_node_exists(self.parent_tag)

    def apply_to_ontology(self):
        self.new_node.save()
        self.parent.children.connect(self.new_node, self.new_relationship.properties)

    def apply_to_knowledge_graph(self):
        # NOTE: This migration doesn't change the knowledge graph because there's no data for the new node yet.
        pass

    @property
    def steps(self):
        return [
            OntologyMigrationStep(migration = self, title = "CREATION", target = self.new_node),
            OntologyMigrationStep(migration = self, title = "LINKING", target = self.new_relationship)
        ]

class InsertionSingleMigration(OntologyMigration):
    title = "INSERTION_SINGLE"

    def __init__(self, relationship_tag: str, new_node: OntologyNode, new_relationship: OntologyRelationship):
        """relationship_tag: Tag of the relationship into which the new node is inserted."""
        self.new_node = new_node
        self.new_relationship = new_relationship
        self.relationship_tag = relationship_tag

    def validate(self):
        self._validate_that_node_doesnt_exist(self.new_node.tag)
        self._validate_that_relationship_doesnt_exist(self.new_relationship.tag)
        
        if self.new_node.node_type == OntologyNodeTypes.LEAF:
            raise OntologyMigrationError("Cannot insert a leaf node into a relationship.")
        
        linked_nodes = self._validate_that_relationship_exists(self.relationship_tag)
        self.start_node: OntologyNode = linked_nodes.start_node
        self.end_node: OntologyNode = linked_nodes.end_node
        self.old_relationship: OntologyRelationship = linked_nodes.relationship
        
    def apply_to_ontology(self):
        # 1. Creation
        self.new_node.save()

        # 2. Linking
        self.start_node.children.connect(self.new_node, self.new_relationship.properties)

        # 3. Unlinking (Relinking) (Unlinking has to happen first because the old relationship tag can only exist once.)
        self.start_node.children.disconnect(self.end_node)

        # 4. Linking (Relinking)
        self.new_node.children.connect(self.end_node, self.old_relationship.properties)


    def apply_to_knowledge_graph(self):
        # TODO: Add attributes to the new node and relationship.
        # The attributes from the old relationships need to be transfered!
        query = "MATCH (n1)-[r:$($old_relationship_tag)]->(n2) " \
                "CREATE (n1)-[:$($new_relationship_tag)]->(n3:$($node_tag))-[:$($old_relationship_tag)]->(n2)" \
                "DELETE r"
        
        parameters = {
            "old_relationship_tag": self.old_relationship.tag,
            "new_relationship_tag": self.new_relationship.tag,
            "node_tag": self.new_node.tag
        }
        
        db.cypher_query(query, parameters)

    @property
    def steps(self):
        return [
            OntologyMigrationStep(migration = self, title = "CREATION", target = self.new_node),
            OntologyMigrationStep(migration = self, title = "LINKING", target = self.new_relationship),
            OntologyMigrationStep(migration = self, title = "RELINKING", target = self.old_relationship),
        ]

class InsertionMultipleMigration(OntologyMigration):
    title = "INSERTION_MULTIPLE"

    def __init__(self, new_node: OntologyNode, 
                 new_relationship: OntologyRelationship,
                 relationship_tags: list[str]):
        self.new_node = new_node
        self.new_relationship = new_relationship
        self.relationship_tags = relationship_tags

    def validate(self):
        self._validate_that_node_doesnt_exist(self.new_node.tag)
        self._validate_that_relationship_doesnt_exist(self.new_relationship.tag)
                
        if self.new_node.node_type == OntologyNodeTypes.LEAF:
            raise OntologyMigrationError("Cannot insert a leaf node into a relationship.")

        start_nodes: set[OntologyNode] = set()
        self.old_links: list[LinkedNodes] = []
        for relationship_tag in self.relationship_tags:
            linked_nodes = self._validate_that_relationship_exists(relationship_tag)
            start_nodes.add(linked_nodes.start_node)
            self.old_links.append(linked_nodes)

        if len(start_nodes) > 1:
            raise OntologyMigrationError(f"All relationships must have the same start node for InsertionMultipleMigration.")
        self.start_node = start_nodes.pop()

    def apply_to_ontology(self):
        # 1. Creation
        self.new_node.save()

        # 2. Linking
        self.start_node.children.connect(self.new_node, self.new_relationship.properties)

        for old_link in self.old_links:
            # 4. Unlinking (Relinking)
            self.start_node.children.disconnect(old_link.end_node)

            # 3. Linking (Relinking)
            self.new_node.children.connect(old_link.end_node, old_link.relationship.properties)


    def apply_to_knowledge_graph(self):
        query = "MATCH (start_node)-[r]->(end_node) " \
        "WHERE TYPE(r) IN $relationship_tags " \
        "MERGE (start_node)-[:$($new_relationship_label)]->(middle_node:$($new_node_label)) " \
        "CREATE (middle_node)-[:`+TYPE(r)+`]->(end_node) " \
        "DELETE r"

        parameters = {
            "relationship_tags": self.relationship_tags,
            "new_relationship_label": self.new_relationship.name,
            "new_node_label": self.new_node.tag
        }

        db.cypher_query(query, parameters)

    @property
    def steps(self):
        return [
            OntologyMigrationStep(migration = self, title = "CREATION", target = self.new_node),
            OntologyMigrationStep(migration = self, title = "LINKING", target = self.new_relationship)
        ] + [
            OntologyMigrationStep(migraiton = self, title = "RELINKING", target = old_link.relationship)
            for old_link in self.old_links
        ]

class ExtensionMigration(OntologyMigration):
    title = "EXTENSION"

    def __init__(self, relationship_tag: str, 
                 inserted_node: OntologyNode, inserted_relationship: OntologyRelationship,
                 added_node: OntologyNode, added_relationship: OntologyRelationship):
        self.relationship_tag = relationship_tag
        self.inserted_node = inserted_node
        self.inserted_relationship = inserted_relationship
        self.added_node = added_node
        self.added_relationship = added_relationship

        self.insertion_migration = InsertionSingleMigration(relationship_tag, inserted_node, inserted_relationship)
        self.addition_migration = AdditionMigration(added_node, added_relationship, inserted_node.tag)

    def validate(self):
        self.insertion_migration.validate()
        self._validate_that_node_doesnt_exist(self.added_node.tag)
        self._validate_that_relationship_doesnt_exist(self.added_relationship.tag)
        if self.inserted_node.tag == self.added_node.tag:
            raise OntologyMigrationError(self, "The inserted connective node and the added leaf node must have differing tags.")
        if self.inserted_relationship.tag == self.added_relationship:
            raise OntologyMigrationError(self, "The new relationships of the inserted connective node and the added leaf node must have differing tags.")

    def apply_to_ontology(self):
        self.insertion_migration.apply_to_ontology()
        self.addition_migration.apply_to_ontology()

    def apply_to_knowledge_graph(self):
        self.insertion_migration.apply_to_knowledge_graph()
        # The addition and attribute modification have no effect on the knowledge graph.

    @property
    def steps(self):
        return self.insertion_migration.steps + self.addition_migration.steps

class PartialDeletionMigration(OntologyMigration):
    title = "DELETION_PARTIAL"

    # TODO: If a node with 1 parent and 1 child is deleted using this migration, it's unclear which relationship is preserved.
    # Currently the child relationships take precedence but this should either be decided and clarified.
    # Possibly the tag of the relationship to be preserved could be added as a constructor argument.
    def __init__(self, tag: str):
        self.tag = tag

    def validate(self):
        self.target = self._validate_that_node_exists(self.tag)
        if self.target.node_type != OntologyNodeTypes.CONNECTIVE:
            raise OntologyMigrationError(self, "Only ontology nodes with node type CONNECTIVE can be deleted by DELETION_PARTIAL.")
        
        self.parent_count = len(self.target.parents.all())
        self.child_count = len(self.target.children.all())

        if self.parent_count > 1 and self.child_count > 1:
            raise OntologyMigrationError(self, "Connective nodes that have more than one child and more than one parent cannot be deleted by DELETION_PARTIAL because it would be unclear how to connect them.")

    def apply_to_ontology(self):
        if self.parent_count == 0 or self.child_count == 0:
            # In this case, there's no need to relink anything.
            self.target.delete()
        elif self.parent_count == 1:
            parent: OntologyNode = self.target.parents.get()
            all_children = get_all_outgoing_relationships(self.target, OntologyNode.get_relationship_label())
            self.target.delete()

            for linked_node in all_children:
                parent.children.connect(linked_node.end_node, linked_node.relationship.properties)
        elif self.child_count == 1:
            child: OntologyNode = self.target.children.get()
            all_parents = get_all_incoming_relationships(self.target, OntologyNode.get_relationship_label())
            self.target.delete()

            for linked_node in all_parents:
                parent: OntologyNode = linked_node.start_node
                parent.children.connect(child, linked_node.relationship.properties)

    # TODO: Here and elsewhere: Relationships and tags are created without initial attributes!
    def apply_to_knowledge_graph(self):
        if self.parent_count == 0 or self.child_count == 0:
            query = "MATCH (n:$($node_tag)) DETACH DELETE n"
        elif self.parent_count == 1:
            # NOTE: I expect that the order of the CREATE and DELETE statements might have to be switched.
            query = "MATCH (start_node)-->(delete_node:$($node_tag))-[r]->(end_node) " \
            "CREATE (start_node)-[:`+TYPE(r)+`]->(end_node)" \
            "DETACH DELETE delete_node"
        elif self.child_count == 1:
            # NOTE: I expect that the order of the CREATE and DELETE statements might have to be switched.
            query = "MATCH (start_node)-[r]->(delete_node:$($node_tag))-->(end_node) " \
            "CREATE (start_node)-[:`+TYPE(r)+`]->(end_node)" \
            "DETACH DELETE delete_node"

        parameters = { "node_tag": self.target.tag }
        db.cypher_query(query, parameters)


class FullDeletionMigration(OntologyMigration):
    title = "DELETION_FULL"

    def __init__(self, tag: str):
        self.tag = tag

    def validate(self):
        self.node = self._validate_that_node_exists(self.tag)

        query = """
        MATCH (n:OntologyNode{tag: $tag})-[*0..]->(x)
        WITH DISTINCT x
        RETURN x
        """
        self.affected_nodes,_ = db.cypher_query(query, {"tag": self.tag}, resolve_objects = True)

    def apply_to_ontology(self):
        query = """
        MATCH (n:OntologyNode{tag: $tag})-[*0..]->(x)
        WITH DISTINCT x
        DETACH DELETE x
        """
        db.cypher_query(query, {"tag": self.tag})

    def apply_to_knowledge_graph(self):
        # I'm sure this query can have no unintended side-effects like accidentally deleting the entire knowledge graph :-)
        query = """
        MATCH (n:{tag})-[*0..]->(x)
        WITH DISTINCT x
        DETACH DELETE x
        """.format(tag = self.tag)
        db.cypher_query(query)

    @property
    def steps(self):
        return [
            OntologyMigrationStep(migration = self, title = "DELETION", target = node)
            for node in self.affected_nodes
        ]

class LeafDeletionMigration(OntologyMigration):
    title = "DELETION_LEAF"

    # NOTE: What's the point of this migration? A FullDeletionMigration on a leaf would also work.
    def __init__(self, tag: str):
        self.tag = tag

    def validate(self):
        self.target = self._validate_that_node_exists(self.tag)
        if self.target.node_type != OntologyNodeTypes.LEAF:
            raise OntologyMigrationError(self, "Only ontology nodes with the type LEAF can be deleted by DELETION_LEAF")

    # TODO: If the parent node turns into a leaf, its node type should maybe be changed.
    def apply_to_ontology(self):
        node: OntologyNode = OntologyNode.nodes.get(tag = self.tag)
        node.delete()

    def apply_to_knowledge_graph(self):
        query = "MATCH (n:$($tag)) DETACH DELETE n"
        parameters = { "tag": self.target.tag }
        db.cypher_query(query, parameters)
