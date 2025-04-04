import secrets
from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .constants import ROLE_CHOICES, SCOPE_CHOICES
from api.schema import UserData, AccessData
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
        default=True,
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
    
    # TODO: Add a field for storing requested permissions
    permissions_requested = models.ManyToManyField(
        Scope,
        blank=True,
        related_name="users_requested",
    )
    
    # TODO: Add a field for storing granted permissions (maybe with django permissions)
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
