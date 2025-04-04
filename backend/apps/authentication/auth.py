from ninja.security import HttpBearer
from .models import Token
from django.utils import timezone
from django.conf import settings


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        request.user = None
        try:
            token_obj = Token.objects.get(key=token)
            if (timezone.now() - token_obj.created).total_seconds() > settings.AUTH_TOKEN_EXPIRY_TIME:
                return None
            request.user = token_obj.user
            return token_obj.user
        except Token.DoesNotExist:
            return None
