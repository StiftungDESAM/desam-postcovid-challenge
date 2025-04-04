from functools import wraps
from typing import List, Union
from ninja.errors import HttpError
import logging

logger = logging.getLogger(__name__)


class PermissionChecker:
    @staticmethod
    def has_permission(permissions: Union[List[str], str], require_all: bool = True):
        """
        Decorator to check if the user has the required permissions.
        
        Args:
            permissions: A string or list of strings representing the required permission(s).
            require_all: If True, the user must have all the specified permissions.
                         If False, having any one of the permissions is sufficient.
        """
        def decorator(view_func):
            @wraps(view_func)
            def wrapper(request, *args, **kwargs):
                user = request.auth
                
                # Superusers have all permissions
                if user.is_superuser:
                    return view_func(request, *args, **kwargs)
                
                # Convert single permission to list for uniform handling
                required_permissions = [permissions] if isinstance(permissions, str) else permissions
                
                # Get the user's granted permissions
                user_permissions = [permission.name for permission in user.permissions_granted.all()]
                
                # Check permissions based on require_all flag
                if require_all:
                    # User must have all required_permissions
                    if all(permission in user_permissions for permission in required_permissions):
                        return view_func(request, *args, **kwargs)
                else:
                    # User needs at least one of the required_permissions
                    if any(permission in user_permissions for permission in required_permissions):
                        return view_func(request, *args, **kwargs)
                
                raise HttpError(403, "Permission denied")
                
            return wrapper
        return decorator