from django.core.management.base import BaseCommand

from authentication.models import Scope, Role
from authentication.constants import get_role_names, get_scope_names

class Command(BaseCommand):
    # NOTE: This command currently only handles the creation of scopes and roles.
    # The case of deletion is intentionally not implemented due to the possible data loss.
    help = "Makes sure the database is properly initialized with the required constants."

    def handle(self, *args, **options):
        self.stdout.write("Initializing database constants...")

        change_detected = False
        change_detected |= self.init_scopes()
        change_detected |= self.init_roles()

        if change_detected:
            self.stdout.write(
                self.style.SUCCESS("Successfully applied changes to the database.")
            )
        else:
            self.stdout.write("No change to the database necessary.")

    def init_scopes(self) -> bool:
        """Makes sure all defined scopes are in the database. Returns if a new scope had to be created or not."""
        created_scope = False
        for scope_name in get_scope_names():
            _, created = Scope.objects.get_or_create(name = scope_name)
            if created:
                self.stdout.write(f"Created new scope '{scope_name}'.")
                created_scope = True
        return created_scope
    
    def init_roles(self) -> bool:
        """Makes sure all defined roles are in the database. Returns if a new role had to be created or not."""
        created_role = False
        for role_name in get_role_names():
            _, created = Role.objects.get_or_create(name = role_name)
            if created:
                self.stdout.write(f"Created new role '{role_name}'.")
        return created_role
        
