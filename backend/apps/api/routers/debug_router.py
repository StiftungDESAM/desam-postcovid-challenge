from api.transactions import TransactionRouter

from django.conf import settings
from ninja.errors import HttpError

from authentication.models import Role, Scope
from authentication.email import test_email

import logging
logger = logging.getLogger(__name__)

router = TransactionRouter()


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
    auth=None,
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
    
  