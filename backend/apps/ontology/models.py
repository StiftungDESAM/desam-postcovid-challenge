
# ! IMPORTANT ! #
# Never import this file as "apps.ontology.models"
# Always import it as "ontology.models"
# Otherwise neomodel thinks you're redefining models and relationships and raises exceptions.

import neomodel
from neomodel import db
from django.db import models

from django.utils import timezone
from typing import Type

class OntologyRelationship(neomodel.StructuredRel):
    name = neomodel.StringProperty(required = True)
    tag = neomodel.StringProperty(required = True, unique_index = True)
    cardinality = neomodel.StringProperty(default = "*")

    created_at = neomodel.DateTimeProperty(default = timezone.now)
    updated_at = neomodel.DateTimeProperty(default = timezone.now)

    @property
    def all_properties(self):
        return {
            "name": self.name,
            "tag": self.tag,
            "cardinality": self.cardinality,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @property
    def properties(self):
        """Only returns properties that are JSON serializable."""
        return {
            "name": self.name,
            "tag": self.tag,
            "cardinality": self.cardinality
        }
    
    @classmethod
    def from_properties(cls, settings: dict):
        return cls(
            name = settings["name"],
            tag = settings["tag"],
            cardinality = settings["cardinality"]
        )

class OntologyNodeTypes(models.TextChoices):
    LEAF = "L", "Leaf"
    STAKEHOLDER = "S", "Stakeholder"
    CONNECTIVE = "C", "Connective"

class OntologyNode(neomodel.StructuredNode):
    uuid = neomodel.UniqueIdProperty()
    name: str = neomodel.StringProperty(required = True)
    tag: str = neomodel.StringProperty(required = True, unique_index = True)
    node_type: OntologyNodeTypes = neomodel.StringProperty(required = True, choices = OntologyNodeTypes.choices)

    created_at: timezone.datetime = neomodel.DateTimeProperty(default = timezone.now)
    updated_at: timezone.datetime = neomodel.DateTimeProperty(default = timezone.now)

    children: neomodel.RelationshipManager = neomodel.RelationshipTo("OntologyNode", "IS_RELATED_TO", model = OntologyRelationship)
    parents: neomodel.RelationshipManager = neomodel.RelationshipFrom("OntologyNode", "IS_RELATED_TO", model = OntologyRelationship)

    @property
    def node_class(self) -> Type[neomodel.StructuredNode]:
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

    @classmethod
    def get_relationship_label(cls) -> str:
        return cls.children.definition["relation_type"]
    
    @property
    def all_properties(self) -> dict:
        return {
            "name": self.name,
            "tag": self.tag,
            "node_type": self.node_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @property
    def properties(self) -> dict:
        """Only returns properties that are JSON serializable."""
        return {
            "name": self.name,
            "tag": self.tag,
            "node_type": self.node_type,
        }

    @classmethod
    def from_properties(cls, settings: dict):
        return cls(
            name = settings["name"],
            tag = settings["tag"],
            node_type = settings["node_type"]
        )
    
    def __hash__(self):
        return hash((self.tag,))
    
    def __eq__(self, other):
        return self.tag == other.tag
