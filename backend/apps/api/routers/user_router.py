from api.transactions import TransactionRouter

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.utils import timezone
from ninja.errors import HttpError

from api import schema
from authentication.models import CustomUser, Role, Scope, Token, TemplateMail, UserCode, CodeType
from authentication.email import send_email, create_verification_link, create_reset_link

import logging
logger = logging.getLogger(__name__)

router = TransactionRouter()

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
    
    verification_code = UserCode.objects.generate(user, CodeType.VERIFICATION)
    
    send_email(
        recipient_list=[credentials['email']], 
        subject=TemplateMail.ACCOUNT_VERIFICATION.subject,
        message=f"{TemplateMail.ACCOUNT_VERIFICATION.message}{create_verification_link(verification_code.code)}",
    )
    
    user.verification_email_sent = timezone.now()
    user.save()

    return 201, { "message": "User registered successfully", "user_id": user.id }

@router.get(
        "/email-verification",
        summary = "Verification of a user account by a code",
        description = "This endpoint receives a code generated during the registration process of a user and verifies the account if the code is correct and not expired",
        auth = None,
        response = {302: None}
)
def verify_email(request):
    try:
        code = request.GET.get("code")
        
        user_code = UserCode.objects.get(code=code, type=CodeType.VERIFICATION)
    except UserCode.DoesNotExist:
        return HttpResponseRedirect("/page?msg=REGISTRATION_FAILED")
    
    if user_code.is_expired():
        user_code.delete()
        return HttpResponseRedirect("/page?msg=CODE_EXPIRED")
    
    user_code.user.is_active = True
    user_code.user.email_verified = True
    user_code.user.save()
    
    send_email(
        recipient_list=[user_code.user.email], 
        subject=TemplateMail.ACCOUNT_VERIFICATION_SUCCESS.subject,
        message=TemplateMail.ACCOUNT_VERIFICATION_SUCCESS.message
    )
    
    user_code.delete()
    
    return HttpResponseRedirect("/page?msg=REGISTRATION_SUCCESSFUL")

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

@router.post(
    "/request-password-reset",
    summary="Requests a password reset",
    description="This endpoint requests a password reset by the user itself. Triggers a email with a code that is used for verification of the process.",
    auth = None,
    response={201: None}
)
def request_password_reset(request, data: schema.RequestPasswordResetSchema):
    try:
        user = CustomUser.objects.get(email=data.email)
    except CustomUser.DoesNotExist:
        return 201, None
        
    reset_code = UserCode.objects.generate(user, CodeType.PASSWORD_RESET)
    
    send_email(
        recipient_list=[data.email], 
        subject=TemplateMail.PASSWORD_RESET.subject,
        message=f"{TemplateMail.PASSWORD_RESET.message}{create_reset_link(reset_code.code)}",
    )

    return 201, None

@router.post(
    "/password-reset",
    summary="Handles the actual password reset",
    description="This endpoint handles the actual password reset by the user itself. Receives the code from the email as well as the new password for the user.",
    auth = None,
    response={200: None, 400: str, 403: str}
)
def password_reset(request, data: schema.PasswordResetSchema):    
    if not data.password:
        raise HttpError(400, "PASSWORD_RESET_FAILED")
    
    try:
        user_code = UserCode.objects.get(code=data.code, type=CodeType.PASSWORD_RESET)
    except UserCode.DoesNotExist:
        raise HttpError(400, "PASSWORD_RESET_FAILED")

    if user_code.is_expired():
        user_code.delete()
        raise HttpError(403, "CODE_EXPIRED")
        
    user_code.user.set_password(data.password)
    user_code.user.save()
    
    send_email(
        recipient_list=[user_code.user.email], 
        subject=TemplateMail.PASSWORD_RESET_SUCCESS.subject,
        message=TemplateMail.PASSWORD_RESET_SUCCESS.message
    )
    
    user_code.delete()
    
    return 200, None

@router.get(
        "/",
        summary = "Get information on the currently logged in user",
        description = "This endpoint gets the user associated with the authentication token in the header.",
        response = {200: schema.UserLoginSchema}
)
def get_user(request):
    return request.user



@router.get(
    "/access-check",
    summary="Check access for a user",
    description="This endpoint checks if the user has the requested permission",
    response={200: None},
)
def check_access(request, permissions: str, require_all: bool = True):
    # Superusers have all permissions
    if request.user.is_superuser:
        return 200, None
    
    permission_list = [x.strip() for x in permissions.split(";")]
  
    # check if the requested permissions are in the list of possible permissions
    if not all(Scope.objects.filter(name=permission).exists() for permission in permission_list):
        raise HttpError(400, "Not all requested permissions are valid permissions.")
    
    has_permission = False
    
    if require_all:
        # User must have all required_permissions
        has_permission = request.user.has_permissions(permission_list)
    else:
        # User needs at least one of the required_permissions
        has_permission = any(request.user.has_permission(permission) for permission in permission_list)
    
    # raise error if the user does not have the required permissions    
    if not has_permission:
        raise HttpError(403, "Required permission not granted")
    
    return 200, None