from django.shortcuts import redirect
from django.utils import timezone

from .decorators import get_vendor_profile
from .models import VendorPortalSession


class VendorPortalIsolationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        vendor_profile = get_vendor_profile(request.user)
        path = request.path or '/'
        if vendor_profile and vendor_profile.is_active:
            allowed_prefixes = (
                '/vendor-portal/',
                '/media/',
                '/static/',
            )
            if not any(path.startswith(prefix) for prefix in allowed_prefixes):
                return redirect('/vendor-portal/')
            if request.session.session_key:
                VendorPortalSession.objects.filter(
                    vendor_user=vendor_profile,
                    session_key=request.session.session_key,
                    is_active=True,
                ).update(last_activity_at=timezone.now())
        return self.get_response(request)
