import secrets
from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .constants import ROLE_CHOICES, SCOPE_CHOICES
from collections import namedtuple
import uuid
from datetime import timedelta
from typing import Union
import logging

logger = logging.getLogger(__name__)

#   Create your models here.
class Gender(models.TextChoices):
        MALE = 'MALE'
        FEMALE = "FEMALE"
        OTHER = "OTHER"
        
# Role Model (Instead of TextChoices)
class Role(models.Model):
    name = models.CharField(
        max_length=50, 
        choices = ROLE_CHOICES, 
        unique=True
    )

    def __str__(self):
        return self.name
    
# Scopes Model (Instead of TextChoices)
class Scope(models.Model):
    name = models.CharField(
        max_length=50,
        choices=SCOPE_CHOICES,
        unique=True
    )

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    #use_in_migrations = True 
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        
        # Extract ManyToMany fields before creating the user
        roles = extra_fields.pop("role", [])
        permissions = extra_fields.pop("permissions_requested", [])
        
        #print(permissions)
        
        # Create user instance
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        '''
        # Set ManyToMany fields AFTER saving
        if roles:
            #r1 = Role(roles)
            user.role.set(roles)
        if permissions:
            user.permissions_requested.set(permissions)
        '''    
        '''
        # Set ManyToMany fields AFTER saving
        if roles:
            # Convert string role names to Role instances if needed
            if all(isinstance(r, str) for r in roles):
                roles = Role.objects.filter(name__in=roles)
            user.role.set(roles)
            
        if permissions:
            # Convert string permission names to Scope instances if needed
            if all(isinstance(p, str) for p in permissions):
                permissions = Scope.objects.filter(name__in=permissions)
            user.permissions_requested.set(permissions)
        '''
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        superuser = self.create_user(email, password, **extra_fields)
        
        #role = Role.objects.filter(name__in="SUPER_ADMIN")
        #permission = Scope.objects.filter(name__in="SUPER_ADMIN")
        
        role = Role.objects.get(name="SUPER_ADMIN")
        permission = Scope.objects.get(name="SUPER_ADMIN")
        
        logger.debug(role)
        logger.debug(permission)
        
        superuser.role.add(role)
        superuser.permissions_granted.add(permission)
        
        return superuser
    
    


class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    
    email = models.EmailField(
        _("email address"), 
        unique=True, 
        max_length=255, 
        blank=False, 
        error_messages={
            "unique": _("A user with that E-Mail already exists.")},
    )
    
    # All these field declarations are copied as-is
    # from `AbstractUser`
    
    first_name = models.CharField(
        _("first name"), 
        max_length=150, 
        blank=True,
    )
    last_name = models.CharField(
        _("last name"), 
        max_length=150, 
        blank=True,
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        _("date joined"), 
        default=timezone.now,
    )
    
    
    # Add additional fields here if needed
    gender = models.CharField(
        _("gender"),
        max_length=10,
        choices = Gender,
        blank=True,
    )
    
    role = models.ManyToManyField(
        Role,
        blank=True,
        related_name="users",
    )
    
    date_of_birth = models.DateField(
        _("date of birth"), 
        null=True, 
        blank=True
    )
    
    # stores date and time when verification email was sent
    verification_email_sent = models.DateTimeField(
        _("verification mail sent"), 
        null=True, 
        blank=True
    )
    
    email_verified = models.BooleanField(
        _("email verified"), 
        default=False
    )
    
    permissions_requested = models.ManyToManyField(
        Scope,
        blank=True,
        related_name="users_requested",
    )
    
    permissions_granted = models.ManyToManyField(
        Scope,
        blank=True,
        related_name="users_granted",
    )
    
    permissions_verified = models.BooleanField(
        _("permissions verified"), 
        default=False
    )
    
    
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
    
    def __str__(self):
        return self.email
    
    def has_permission(self, permission_name: str) -> bool:
        """
        Check if the user has a specific permission.
        """
        return self.permissions_granted.filter(name=permission_name).exists()
    
    
    def has_permissions(self, permission_names: Union[list[str], str]) -> bool:
        """
        Check if the user has all the specified permission.
        """
        required_permissions = [permission_names] if isinstance(permission_names, str) else permission_names
        
        return all(self.permissions_granted.filter(name=permission_name).exists() for permission_name in required_permissions)
        
        
    
    # TODO: Add method for sending verification email
    def send_verification_email(self):
        pass

class Token(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True)
    # expiration is handled by the AuthBearer class in ../authentication/auth.py
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return secrets.token_hex(32)

    def __str__(self):
        return self.key


class CodeType(models.TextChoices):
    VERIFICATION = "VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"

class UserCodeManager(models.Manager):
    def generate(self, user, code_type):
        from datetime import timedelta
        from django.utils import timezone

        expiration_times = {
            CodeType.VERIFICATION: timedelta(days=7),
            CodeType.PASSWORD_RESET: timedelta(minutes=30),
        }
        
        created_at = timezone.now()
        expires_at = created_at + expiration_times.get(code_type, timedelta(minutes=30))

        # Check for existing code of same type
        new_code, created = self.get_or_create(
            user=user,
            type=code_type,
            defaults={
                "expires_at": expires_at,
                "created_at": created_at,
                "code": uuid.uuid4(),
            }
        )

        # Update the existing code
        if not created:
            new_code.code = uuid.uuid4()
            new_code.expires_at = expires_at
            new_code.created_at = created_at
            new_code.save()

        return new_code
    
class UserCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    type = models.CharField(max_length=30, choices=CodeType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    objects = UserCodeManager()

    def is_expired(self):
        return timezone.now() > self.expires_at  


    
EmailTemplate = namedtuple("EmailTemplate", ["subject", "message"])

class TemplateMail:
    ACCOUNT_VERIFICATION = EmailTemplate(
        subject="Verifikation Ihres MEVODAT - Post-Covid Datenplattform Accounts",
        message=(
            "Willkommen auf der MEVODAT - Post-Covid Datenplattform!<br/>"
            "Bitte bestätigen Sie Ihre E-Mail-Adresse, indem Sie auf den folgenden Link klicken.<br/>"
        )
    )
    ACCOUNT_VERIFICATION_SUCCESS = EmailTemplate(
        subject="Ihr MEVODAT - Post-Covid Datenplattform Account wurde verifiziert",
        message=(
            "Willkommen auf der MEVODAT - Post-Covid Datenplattform!<br/>"
            "Ihr Account ist nun verifiziert und Sie können sich ab sofort mit Ihren Zugangsdaten anmelden."
        )
    )
    PASSWORD_RESET = EmailTemplate(
        subject="Zurücksetzung des Passworts Ihres MEVODAT - Post-Covid Datenplattform Accounts",
        message=(
            "Sie haben eine Zurücksetzung Ihres Passworts für die MEVODAT - Post-Covid Datenplattform angefordert.<br/>"
            "Bitte klicken Sie auf den folgenden Link, um ein neues Passwort festzulegen.<br/>"
            "Wenn Sie diese Anfrage nicht gestellt haben, ignorieren Sie bitte diese E-Mail.<br/>"
        )
    )
    PASSWORD_RESET_SUCCESS = EmailTemplate(
        subject="Das Passwort Ihres MEVODAT - Post-Covid Datenplattform Accounts wurde geändert",
        message=(
            "Das Passwort Ihres Accounts wurde erfolgreich geändert.<br/>"
            "Sollten Sie dies nicht veranlasst haben, dann kontaktieren Sie uns bitte."
        )
    )
    PERMISSION_VERIFICATION = EmailTemplate(
        subject="Ihre angefragten Funktionalitäten für die MEVODAT - Post-Covid Datenplattform wurden freigeschaltet",
        message=(
            "Ihre angefragten Funktionalitäten für die MEVODAT - Post-Covid Datenplattform wurden freigeschaltet.<br/>"
            "Sie können diese nun nach der nächsten Anmeldung nutzen."
        )
    )
    ACCOUNT_DELETION = EmailTemplate(
        subject="Löschung Ihres MEVODAT - Post-Covid Datenplattform Accounts",
        message=(
            "Ihr Account wurde von einem Admin gelöscht.<br/>"
            "Sollte es sich hierbei um einen Fehler handeln, dann kontaktieren Sie uns bitte."
        )
    )