from django.contrib.auth import authenticate
from ninja import NinjaAPI
from ninja.errors import HttpError
from neomodel import db
from uuid import uuid4
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.utils import timezone
from ninja.responses import codes_4xx

from . import schema
from .schema import Message
from .permissions import PermissionChecker
#from .utils import parse_user_for_admin_query



from authentication.auth import AuthBearer
import logging


api = NinjaAPI(auth=AuthBearer())
logger = logging.getLogger(__name__)



api.add_router("admin/", "api.routers.admin_router.router", tags = ["Admin"])

api.add_router("user/", "api.routers.user_router.router", tags = ["User"])

api.add_router("data/", "api.routers.knowledge_router.router", tags = ["Knowledge graph"])

api.add_router("ontology/", "api.routers.ontology_router.router", tags = ["Ontology"])

api.add_router("debug/", "api.routers.debug_router.router", tags = ["Debug"])
