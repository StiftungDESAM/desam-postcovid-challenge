from django.core.management.base import BaseCommand
from neomodel.sync_.core import db

from knowledge.models import load_all_knowledge_node_classes

class Command(BaseCommand):
    help = "Installs all neomodel class labels in the database."

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.NOTICE('Migrating graph database by removing and re-installing all labels.')
        )
        load_all_knowledge_node_classes()
        db.remove_all_labels(self.stdout)
        self.stdout.write(
            self.style.SUCCESS('Successfully removed all labels.')
        )

        db.install_all_labels(self.stdout)
        self.stdout.write(
            self.style.SUCCESS('Successfully installed all labels.')
        )
