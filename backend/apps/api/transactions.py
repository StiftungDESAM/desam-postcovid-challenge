import ninja
from django.db import transaction as django_transaction
import neomodel

from functools import wraps

def combined_transaction(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        with django_transaction.atomic():
            with neomodel.db.transaction:
                return func(request, *args, **kwargs)
    return wrapper


class TransactionRouter(ninja.Router):
    def add_api_operation(self, path, methods, view_func, *args, **kwargs):
        wrapped_view = combined_transaction(view_func)
        return super().add_api_operation(path, methods, wrapped_view, *args, **kwargs)
