from functools import wraps

from django.core.exceptions import PermissionDenied

from .utils import is_admin_like, require_authenticated


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        redirect_response = require_authenticated(request)
        if redirect_response:
            return redirect_response
        if not is_admin_like(request.user):
            raise PermissionDenied('Admin access required.')
        return view_func(request, *args, **kwargs)

    return _wrapped_view

