from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from permissions.utils import is_admin_like


def get_vendor_profile(user):
    if not getattr(user, 'is_authenticated', False):
        return None
    return getattr(user, 'vendor_profile', None)


def require_vendor_user(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url='/vendor-portal/login/')
        vendor_profile = get_vendor_profile(request.user)
        if not vendor_profile or not vendor_profile.is_active:
            raise PermissionDenied('Vendor portal access required.')
        request.vendor_profile = vendor_profile
        return view_func(request, *args, **kwargs)
    return _wrapped


def require_internal_admin(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url='/admin/login/')
        if getattr(request.user, 'vendor_profile', None):
            raise PermissionDenied('Vendor users cannot access this page.')
        if not (request.user.is_staff or request.user.is_superuser or is_admin_like(request.user)):
            raise PermissionDenied('Internal admin access required.')
        return view_func(request, *args, **kwargs)
    return _wrapped
