from ninja import Router
from ninja.errors import HttpError
from django.conf import settings
from django.shortcuts import get_object_or_404

from api import schema
from api.schema import Message
from api.permissions import PermissionChecker

from authentication.models import CustomUser, Role, Scope, Token
import logging


logger = logging.getLogger(__name__)

router = Router()


# TODO: Add endpoint to verify permissions
# TODO: Implement authentication/permission checks
@router.post(
    "/users/{email}/verify-permissions",
    summary="Verify user permissions",
    description="This endpoint verifies the permissions requested by a user",
    response={200: Message}
)
@PermissionChecker.has_permission(["ADMIN"])
def verify_permissions(request, email: str, permission_names: schema.PermissionsVerificationSchema):
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")
    
    # TODO: check for authentication
    # check if request.user is authenticated
    # if not, return 401
    
    permission_names = permission_names.dict()["permissions"]
    email = email.lower()
    
    # TODO: implement check for super admin privileges if "ADMIN" is in the list of permissions
    if "ADMIN" in permission_names:
        logger.debug("Checking for super admin privileges")
        # check if request.user has super admin privileges
        # if not, return 403
        
    # get the user based on email address
    user = get_object_or_404(CustomUser, email=email)
    
    # TODO: implement check if user has already verified admin permissions, 
    # if yes, check for super admin privileges of request.user?
    
    # get the permissions requested to be verified
    permissions = Scope.objects.filter(name__in=permission_names)
    
    # check if all permissions were found
    if len(permissions) != len(permission_names):
        raise HttpError(400, "Not all permissions were found in list of available permissions.")
        
    user.permissions_granted.set(permissions)
    
    user.permissions_verified = True
    user.save()
    #permissions = permissions.model_dump()
    #permissions = permissions.pop("permissions", [])
    
    #logger.debug(permissions)
    #logger.debug(email)
    logger.debug(permissions)

    return 200, {"message": f"Permissions verified for {email}: {permission_names}"}                


# TODO: Add authentication/permission checks
@router.delete(
    "/users/{email}",
    summary="Delete user by email",
    description="Deletes a user based on their email address",
    response={204: None}
)
@PermissionChecker.has_permission(["ADMIN"])
def delete_user_by_email(request, email: str):
    """Delete a user by their email address."""
    '''
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    '''
    # Normalize email
    email = email.lower().strip()

    user = get_object_or_404(CustomUser, email=email)
    user.delete()

    return 204, None


# TODO: Add authentication/permission checks
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


# TODO: Add authentication/permission checks
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