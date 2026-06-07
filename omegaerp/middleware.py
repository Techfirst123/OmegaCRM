from django.shortcuts import redirect


class VendorPortalHostRedirectMiddleware:
    vendor_host_marker = 'omega-vendor-portal'
    allowed_prefixes = (
        '/vendor-portal/',
        '/api/vendor-portal/',
        '/static/',
        '/favicon.ico',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':', 1)[0].lower()
        path = request.path_info or '/'
        if self.vendor_host_marker in host and not path.startswith(self.allowed_prefixes):
            return redirect('/vendor-portal/login/')
        return self.get_response(request)
