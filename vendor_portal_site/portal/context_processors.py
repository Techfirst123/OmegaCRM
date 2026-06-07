from django.conf import settings


def portal_branding(_request):
    return {
        'portal_brand_name': settings.PORTAL_BRAND_NAME,
        'portal_app_subtitle': settings.PORTAL_APP_SUBTITLE,
        'portal_support_email': settings.PORTAL_SUPPORT_EMAIL,
        'portal_public_url': settings.PORTAL_PUBLIC_URL,
        'portal_primary_color': settings.PORTAL_PRIMARY_COLOR,
    }
