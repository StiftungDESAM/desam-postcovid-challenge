from api.transactions import TransactionRouter

from django.utils import timezone
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from api import schema
from api.permissions import PermissionChecker
from authentication.email import create_reset_link, create_verification_link, send_email
from authentication.models import CodeType, CustomUser, Role, Scope, Gender, TemplateMail, UserCode

from datetime import date

import logging
logger = logging.getLogger(__name__)

router = TransactionRouter()

@router.get(
    "/users",
    summary="Get all users",
    description="Retrieve a list of all registered users for admin panel",
    response={200: list[schema.UserQuerySchema]}
)
@PermissionChecker.has_permission("ADMIN")
def get_all_users_admin(request):
    """Fetch all users with their details, including roles and permissions."""
    return 200, CustomUser.objects.all()     

@router.get(
    "/users/{email}",
    summary="Get user by email",
    description="Retrieve user query details of a user using their email address",
    response={200: schema.UserQuerySchema}
)
@PermissionChecker.has_permission("ADMIN")
def get_user_by_email_admin(request, email: str):
    """Fetch a user by their email address and return details including roles and permissions."""
    
    email = email.lower().strip()
    user = get_object_or_404(CustomUser, email=email)
    
    return 200, user

@router.post(
    "/users/{email}/verify-permissions",
    summary="Verify user permissions",
    description="This endpoint verifies the permissions requested by a user",
    response={200: schema.Message}
)
@PermissionChecker.has_permission(["ADMIN"])
def verify_permissions(request, email: str, permission_names: schema.PermissionsVerificationSchema):
    permission_names = permission_names.dict()["permissions"]
    email = email.lower().strip()
    
    user = get_object_or_404(CustomUser, email=email)
    
    check_super_admin_permissions(request.user.is_superuser, user.is_superuser, permission_names)
        
    # get the permissions requested to be verified
    permissions = Scope.objects.filter(name__in=permission_names)
    
    # check if all permissions were found
    if len(permissions) != len(permission_names):
        raise HttpError(400, "Invalid permissions requested")
        
    user.permissions_granted.set(permissions)
    user.permissions_verified = True
    user.save()
    
    send_email(
        recipient_list=[email], 
        subject=TemplateMail.PERMISSION_VERIFICATION.subject,
        message=TemplateMail.PERMISSION_VERIFICATION.message,
    )

    return 200, {"message": f"Permissions verified for {email}: {permission_names}"}                


@router.post(
    "/users/{email}/resend-verification",
    summary="Re-sends the verification email for a user",
    description="This endpoint re-sends the verification email for a user. This sends a email to the user with a link that he can use.",
    response={201: None}
)
@PermissionChecker.has_permission(["ADMIN"])
def resend_verification(request, email: str):
    email = email.lower().strip()
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        raise HttpError(400, "Invalid email address")
    
    check_super_admin_permissions(request.user.is_superuser, user.is_superuser, [])
    
    verification_code = UserCode.objects.generate(user, CodeType.VERIFICATION)
    
    send_email(
        recipient_list=[email], 
        subject=TemplateMail.VERIFICATION.subject,
        message=f"{TemplateMail.VERIFICATION.message}{create_verification_link(verification_code.code)}",
    )
    
    user.verification_email_sent = timezone.now()
    user.save()

    return 201, None


@router.post(
    "/users/{email}/request-password-reset",
    summary="Requests a password reset email for a user",
    description="This endpoint requests a password reset email for a user. This sends a email to the user with a link that he can use.",
    response={201: None}
)
@PermissionChecker.has_permission(["ADMIN"])
def request_password_reset(request, email: str):
    email = email.lower().strip()
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        raise HttpError(400, "Invalid email address")
    
    check_super_admin_permissions(request.user.is_superuser, user.is_superuser, [])
    
    reset_code = UserCode.objects.generate(user, CodeType.PASSWORD_RESET)
    
    send_email(
        recipient_list=[email], 
        subject=TemplateMail.PASSWORD_RESET.subject,
        message=f"{TemplateMail.PASSWORD_RESET.message}{create_reset_link(reset_code.code)}",
    )

    return 201, None


@router.delete(
    "/users/{email}",
    summary="Delete user by email",
    description="Deletes a user based on their email address",
    response={204: None}
)
@PermissionChecker.has_permission(["ADMIN"])
def delete_user_by_email(request, email: str):
    email = email.lower().strip()

    user = get_object_or_404(CustomUser, email=email)
    
    # Prevent super users being deleted
    if(user.is_superuser):
        raise HttpError(403, "Super Admins can't be deleted")
    
    user.is_active = False
    user.save()
    
    send_email(
        recipient_list=[email], 
        subject=TemplateMail.ACCOUNT_DELETION.subject,
        message=TemplateMail.ACCOUNT_DELETION.message,
    )

    return 204, None

@router.patch(
    "/users/{email}",
    summary="Update user by email",
    description="Update a user's details using their email address",
    response={200: None},
)
@PermissionChecker.has_permission(["ADMIN"])
def update_user_by_email(request, email: str, user_data: schema.AdminUserUpdateSchema):
    email = email.lower().strip()
    
    user_to_change = get_object_or_404(CustomUser, email=email)
    
    check_super_admin_permissions(request.user.is_superuser, user_to_change.is_superuser, user_data.access.permissions_granted)
    
    check_for_invalid_values(user_data)
    
    user_to_change.first_name = user_data.user.first_name
    user_to_change.last_name = user_data.user.last_name
    user_to_change.date_of_birth = user_data.user.date_of_birth
    user_to_change.gender = user_data.user.gender
    
    user_to_change.role.set(Role.objects.filter(name__in=user_data.access.role))
    user_to_change.permissions_granted.set(Scope.objects.filter(name__in=user_data.access.permissions_granted))
    
    user_to_change.email_verified = user_data.account_verification == "VERIFIED"
    
    user_to_change.save()
    
    return 200, None


def check_super_admin_permissions(requester, target, permissions):
    # Prevent super users being edited by any other user that isn't a super user
    if(target and not requester):
        raise HttpError(403, "Only super admins can edit other super admins")
    
    # Prevent that SUPER_ADMIN can be set as permission and that other users can set admins except the super admin
    if "SUPER_ADMIN" in permissions or ("ADMIN" in permissions and not requester):
        raise HttpError(403, "Setting permission for user with current permissions not allowed")


def check_for_invalid_values(user_data):
    if len(user_data.user.first_name) == 0 or len(user_data.user.last_name) == 0:
        raise HttpError(400, "Invalid name")
    
    if not dob_is_valid(user_data.user.date_of_birth):
        raise HttpError(400, "Invalid date of birth")
    
    if user_data.user.gender not in Gender.values:
        raise HttpError(400, "Invalid gender")
    
    
    valid_roles = list(Role.objects.values_list("name", flat=True))
    for role in user_data.access.role:
        if role not in valid_roles:
            raise HttpError(400, "Invalid role")
        
    valid_permissions = list(Scope.objects.values_list("name", flat=True))
    for permission in user_data.access.permissions_granted:
        if permission not in valid_permissions:
            raise HttpError(400, "Invalid permission")
        
    if user_data.account_verification not in ["VERIFIED", "NOT_VERIFIED", "CODE_EXPIRED"]:
        raise HttpError(400, "Invalid verification status")

def dob_is_valid(dob: date | None) -> bool:
    if dob is None:
        return False
    
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return 18 <= age <= 120
