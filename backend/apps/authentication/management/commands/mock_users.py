from django.core.management.base import BaseCommand
from django.conf import settings

from authentication.models import CustomUser, Gender, Scope, Role
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = "Creates a set of mock users for testing."

    def add_arguments(self, parser):
        parser.add_argument("--verified", 
            action="store_true", 
            help="If this argument is provided, all users are created with verified permissions."
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stderr.write(
                self.style.ERROR('Creating mock users is only permitted in DEBUG mode.')
            )
            return
        
        super_admin_scopes = Scope.objects.all()
        admin_scopes = Scope.objects.exclude(name__contains = "SUPER_ADMIN")
        user_scopes = Scope.objects.exclude(name__contains = "ADMIN")

        for role in Role.objects.all():
            is_super_admin = "SUPER_ADMIN" == role.name
            is_admin = "ADMIN" == role.name
            properties = {
                "email": role.name.lower().replace(" ", "_") + "@example.com",
                "first_name": role.name.capitalize().replace(" ", ""),
                "last_name": "Lastname",
                "gender": random.choice(Gender.values),
                "date_of_birth": date(1950, 1, 1) + timedelta(days = random.randint(0, 365*50)),
                "email_verified": True,
                "is_active": True,
                "permissions_verified": options["verified"] or is_super_admin,
                "password": "x"
            }

            if is_super_admin:
                user: CustomUser = CustomUser.objects.create_superuser(**properties)
                user.permissions_granted.set(super_admin_scopes)
            elif is_admin:
                properties['is_staff'] = True
                user: CustomUser = CustomUser.objects.create_user(**properties)
                if options["verified"]:
                    user.permissions_granted.set(admin_scopes)
                else:
                    user.permissions_requested.set(admin_scopes)
            else:
                user: CustomUser = CustomUser.objects.create_user(**properties)
                if options["verified"]:
                    user.permissions_granted.set(user_scopes)
                else:
                    user.permissions_requested.set(user_scopes)
            user.role.set([role])
            
            self.stdout.write(
                self.style.SUCCESS(f"Created test user '{user.email}' with password 'x'.")
            )
        
