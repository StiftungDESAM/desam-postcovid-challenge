from django.core.management.base import BaseCommand
from neomodel import db

from ontology.data_requests import create_baseline_ontology
from ontology.models import OntologyNode

class Command(BaseCommand):
    help = "Creates the baseline ontology for studies in the graph database."

    def handle(self, *args, **kwargs):
        if len(OntologyNode.nodes.all()) > 0:
            self.stdout.write(
                self.style.NOTICE("Skipping ontology initialization because there's already an ontology in the database.")
            )
            return

        self.stdout.write(
            self.style.NOTICE('Creating baseline ontology...')
        )
        created_nodes = create_baseline_ontology()
        node_count = len(created_nodes)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created baseline ontology consisting of {node_count} ontology nodes.')
        )
