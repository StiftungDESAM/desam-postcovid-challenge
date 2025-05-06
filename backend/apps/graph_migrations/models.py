from django.db import models

from .operations import GraphMigration
from reviewer.models import ReviewDetails

# This is a semi-ugly way to persist graph migrations in the relational database.
# Settings are simply stored as JSON.
class GraphMigrationSettings(models.Model):
    review_details = models.ForeignKey(ReviewDetails, on_delete = models.CASCADE, related_name = "migrations")
    index = models.IntegerField()
    name = models.CharField(max_length = 100)
    settings = models.JSONField()

    @classmethod
    def from_migration(cls, migration: GraphMigration):
        return cls(name = migration.name, settings = migration.to_settings())
    
    def to_migration(self) -> GraphMigration:
        MigrationClass = GraphMigration.migration_class_by_name(self.name)
        migration = MigrationClass.from_settings(self.settings)
        migration.unique_id = self.index
        return migration
    
    def __str__(self):
        return f"{self.name} #{self.index}"

    class Meta:
        ordering = ["review_details", "index"]
    