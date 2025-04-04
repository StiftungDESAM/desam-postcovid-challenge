from ninja import Router
from api import schema
from api.permissions import PermissionChecker
from ninja.errors import HttpError
from django.conf import settings
from django.forms.models import model_to_dict
from authentication.models import CustomUser, Role, Scope
from authentication.email import test_email
import logging


logger = logging.getLogger(__name__)

router = Router()


@router.get(
    "/hello",
    auth=None,
    summary = "Test endpoint",
    description = "You can call this endpoint to verify that the API is working correctly",
)
def hello(request):
    return 200, "Hello, world!"


@router.post(
    "/test_email",
    summary = "Create email for testing",
    response = {201: None}
)
def post_email(request,email_recepient :str):
    try:
        test_email(request,email_recepient)
    except ConnectionRefusedError:
        raise HttpError(503,f"Failed to send email to {email_recepient}, Connection got refused")

    return 201, None

@router.get(
    "/check-roles-and-scopes",
    summary="Check available roles and scopes",
    description="This endpoint lists all available roles and scopes in the database",
    auth=None,
    response={200: dict}
)
def check_roles_and_scopes(request):
    
    if not settings.DEBUG:
        raise HttpError(403, "This endpoint is only available in DEBUG mode.")

    roles = list(Role.objects.values_list('name', flat=True))
    scopes = list(Scope.objects.values_list('name', flat=True))

    return {
        "roles": roles,
        "scopes": scopes,
        "roles_count": len(roles),
        "scopes_count": len(scopes)
    }
