from ninja import Router
from authentication.models import CustomUser, Role, Scope, Token
from ninja.errors import HttpError
from api import schema
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate

import logging


logger = logging.getLogger(__name__)

router = Router()


@router.post(
    "/registration",
    summary = "Register a new user",
    description= "This endpoint registers a new user with the given data",
    auth=None,
    response= {201: dict}
)
def register_user(request, data: schema.UserRegistrationSchema):
    
    # Convert schema data correctly
    user_data = data.user.model_dump()
    access_data = data.access.model_dump()
    credentials = data.credentials.model_dump()

    # Extract role names and permission names
    role_names = access_data.pop("role", [])
    #role_names = [role.upper() for role in access_data.pop("role", [])]  # Ensure uppercase

    permission_names = access_data.pop("permissions_requested", [])
    #permission_names = [perm.upper() for perm in access_data.pop("permissions_requested", [])]  # Ensure uppercase

    admin_string = {"ADMIN", "SUPER_ADMIN"}


    if any(item in admin_string for item in permission_names):
        raise HttpError(400, "ADMIN and SUPER_ADMIN permissions cannot be requested.")
    
    if any(item in admin_string for item in role_names):
        raise HttpError(400, "ADMIN and SUPER_ADMIN role cannot be requested.")

    # Normalize email
    credentials['email'] = credentials['email'].lower().strip()

    # try to get roles and permissions
    roles = Role.objects.filter(name__in=role_names)
    permissions = Scope.objects.filter(name__in=permission_names)

    if len(roles) != len(role_names):
        raise HttpError(400, f"Not all roles were found. Requested roles: {role_names}, Found: {[r.name for r in roles]}")
    
    if len(permissions) != len(permission_names):
        raise HttpError(400, f"Not all permissions were found. Requested permissions: {permission_names}, Found: {[p.name for p in permissions]}")
    
    if CustomUser.objects.filter(email = data.credentials.email).exists():
        raise HttpError(409, "This email address is already in use.")

    # Create user with the provided data
    user = CustomUser.objects.create_user(
        **credentials,  # email and password
        **user_data,  # first_name, last_name, birth
    )    
    
    # Assign ManyToMany roles and permissions_requested
    user.role.set(roles)
    user.permissions_requested.set(permissions)
    logger.debug(permissions)

    return 201, { "message": "User registered successfully", "user_id": user.id }



@router.post(
    "/login",
    summary="Login a user",
    description="This endpoint is used to login a user and returns a token along side some user specific information.",
    auth=None,
    response={200: schema.UserLoginSchema}
)
def login_user(request, login_data: schema.CredentialsData):
    user: CustomUser = authenticate(request, username=login_data.email.lower().strip(), password=login_data.password)

    if user is None:
        raise HttpError(401, "Unauthorized")
    
    if not user.email_verified:
        raise HttpError(403, "Email isn't verified")

    token, _ = Token.objects.get_or_create(user=user)

    # Token exists but is expired, create a new one
    if (timezone.now() - token.created).total_seconds() > settings.AUTH_TOKEN_EXPIRY_TIME:
        token.delete()
        token = Token.objects.create(user=user)
    
    return 200, user


@router.post(
    "/logout",
    summary="Logout a user",
    description="This endpoint is used to logout a user and delete the token.",
    response={204: None}
)
def logout_user(request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token_key = auth_header.split(' ')[1]
        Token.objects.filter(key=token_key).delete()

    return 204, None


@router.get(
        "/",
        summary = "Get information on the currently logged in user",
        description = "This endpoint gets the user associated with the authentication token in the header.",
        response = {200: schema.UserLoginSchema}
)
def get_user(request):
    return request.user
