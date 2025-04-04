
# ! IMPORTANT ! #
# Never import this file as "apps.ontology.models"
# Always import it as "ontology.models"
# Otherwise neomodel thinks you're redefining models and relationships and raises exceptions.

import neomodel
from neomodel.sync_.core import db
from django.utils import timezone
from django.db.models import TextChoices
from typing import Type

class OntologyRelationship(neomodel.StructuredRel):
    name = neomodel.StringProperty(required = True)
    tag = neomodel.StringProperty(required = True, unique_index = True)
    cardinality = neomodel.StringProperty(default = "*")

    created_at = neomodel.DateTimeProperty(default = timezone.now)
    updated_at = neomodel.DateTimeProperty(default = timezone.now)

    @property
    def properties(self):
        return {
            "name": self.name,
            "tag": self.tag,
            "cardinality": self.cardinality,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class OntologyNodeTypes(TextChoices):
    LEAF = "L", "Leaf"
    STAKEHOLDER = "S", "Stakeholder"
    CONNECTIVE = "C", "Connective"

class OntologyNode(neomodel.StructuredNode):
    name: str = neomodel.StringProperty(required = True)
    tag: str = neomodel.StringProperty(required = True, unique_index = True)
    node_type: OntologyNodeTypes = neomodel.StringProperty(required = True, choices = OntologyNodeTypes.choices)

    created_at: timezone.datetime = neomodel.DateTimeProperty(default = timezone.now)
    updated_at: timezone.datetime = neomodel.DateTimeProperty(default = timezone.now)

    children: neomodel.RelationshipManager = neomodel.RelationshipTo("OntologyNode", "IS_RELATED_TO", model = OntologyRelationship)
    parents: neomodel.RelationshipManager = neomodel.RelationshipFrom("OntologyNode", "IS_RELATED_TO", model = OntologyRelationship)

    def _load_node_class(self) -> neomodel.StructuredNode:
        """Loads the knowledge node class from the registry or creates it if it doesn't exist yet."""
        # We must only create knowledge node classes for ontology nodes that have been commited to the database.
        # If element_id is not set, this means that this isn't the case for this ontology node.
        if not self.element_id:
            return None
        
        # Looks in the node registry if the node class has been created already.
        for label_set, definition in db._NODE_CLASS_REGISTRY.items():
            if self.tag in label_set:
                return definition
            
        # If not, it's created and added to the node registry.
        from knowledge.models import load_knowledge_node_class
        return load_knowledge_node_class(self)

    @property
    def node_class(self) -> Type[neomodel.StructuredNode]:
        """Returns the knowledge node class associated with this ontology node.
        This requires the node to be saved to the database."""
        # Tries to load the node class if it hasn't been loaded for this instance yet.
        if not hasattr(self, "_node_class") or self._node_class is None:
            self._node_class = self._load_node_class()
        if self._node_class is None:
            raise ValueError("Couldn't load node class associated with this ontology node. Has it been saved to the database yet?")
        return self._node_class

    @classmethod
    def get_relationship_label(cls):
        return cls.children.definition["relation_type"]
    
    def __hash__(self):
        return hash((self.tag,))
    
    def __eq__(self, other):
        return self.tag == other.tag
