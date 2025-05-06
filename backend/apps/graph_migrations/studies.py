import re
import uuid
import itertools

from .operations import GraphMigration, GraphMigrationStep, AdditionMigration
from .models import GraphMigrationSettings
from ontology.models import OntologyNode, OntologyNodeTypes, OntologyRelationship
from ontology.diff import UMLAUTS_MAPPING
from study.models import Study, CodeBookColumn

def generate_tag_name(column_name: str):
    """Replaces certain special characters like äöüß with ascii and removes all special characters, including spaces."""
    name = column_name.translate(UMLAUTS_MAPPING)
    return re.sub("[^A-Za-z]+", "", name)

def get_migrations_for_study(study: Study) -> list[GraphMigration]:
    migrations: list[GraphMigration] = []
    metadata_columns = CodeBookColumn.objects.filter(codebook__study = study)

    # What new metadata fields have to be created for this study?
    new_meta_fields = metadata_columns.filter(assigned_meta_tag__isnull = True)

    for migration_id, codebook_column in enumerate(new_meta_fields, 1):
        new_node = OntologyNode(
            tag = generate_tag_name(codebook_column.header),
            name = codebook_column.header,
            node_type = OntologyNodeTypes.LEAF
        )
        new_relationship = OntologyRelationship(
            tag = str(uuid.uuid4()),
            name = "hat",
            cardinality = "1"
        )
        new_migration = AdditionMigration(new_node, new_relationship, parent_tag = "Metadaten")
        new_migration.unique_id = migration_id
        migrations.append(new_migration)

    # NOTE: Existing metadata fields require not changes to the ontology and therefore no migrations.
    # NOTE: If necessary, we could implement a validation step here that checks if all metadata tags given
    # NOTE: in the mapping are actually valid sub-nodes of the metadata node or not.
    # metadata_node: OntologyNode = OntologyNode.nodes.get(tag = "Metadaten")
    # existing_meta_fields = metadata_columns.filter(assigned_meta_tag__isnull = False)
    # existing_meta_tags = existing_meta_fields.values_list("assigned_meta_tag", flat=True)
    # ... Check if each a sub-node with each tag actually exists.

    return migrations

def get_migration_steps(migrations: list[GraphMigration]):
    # Generates a flat list of migration steps from all migrations.
    steps = [migration.steps for migration in migrations]
    flattened_list = list(itertools.chain.from_iterable(steps))

    # Adds indices to all migrations for easier distinction.
    for i, step in enumerate(flattened_list, 1):
        step.id = i
    return flattened_list

def save_migrations(study: Study):
    migrations = get_migrations_for_study(study)
    review_details = study.ontology_review.details

    migration_settings_list = []
    for i, migration in enumerate(migrations, 1):        
        migration.validate()
        migration_settings = GraphMigrationSettings.from_migration(migration)
        migration_settings.index = i
        migration_settings.review_details = review_details
        migration_settings_list.append(migration_settings)

    GraphMigrationSettings.objects.bulk_create(migration_settings_list)

def load_migrations(study: Study) -> list[GraphMigration]:
    review_details = study.ontology_review.details
    return [
        migration_settings.to_migration()
        for migration_settings in review_details.migrations.all()
    ]