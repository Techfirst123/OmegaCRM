from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.static import serve as static_serve
from search.views import api_chat, api_search
import os

admin.site.site_header = 'OmegaERP Admin Panel'
admin.site.site_title = 'OmegaERP Admin Panel'
admin.site.index_title = 'OmegaERP Administration'

_REACT_DIST = os.path.join(settings.BASE_DIR, 'frontend', 'dist')


@ensure_csrf_cookie
def _react_index(request, **kwargs):
    index_path = os.path.join(_REACT_DIST, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/html')


urlpatterns = [
    path('admin/', admin.site.urls),

    # AI Assistant API
    path('api/chat/', api_chat, name='api_chat'),
    path('api/search/', api_search, name='api_search'),

    # Session auth API for the React app
    path('api/auth/', include('accounts.urls')),

    # Django backend modules (templates + JSON endpoints)
    path('administration/', include('administration.urls')),
    path('procurement/', include('purchase_orders.urls')),
    path('procurement/vendors/', include('vendors.urls')),
    path('procurement/reports/', include('reports.urls')),
    path('vendor-control/', include('vendors.management_urls')),

    # Root '/' → React app (must come before the core.urls include)
    path('', _react_index),

    # Core routes (vendors/list, projects, materials, vendor AJAX APIs)
    path('', include('core.urls')),

    # React build assets — served from frontend/dist/assets/
    re_path(r'^assets/(?P<path>.*)$', static_serve,
            {'document_root': os.path.join(_REACT_DIST, 'assets')}),

    # Catch-all: any route not matched by Django serves the React app
    # (React Router handles client-side navigation from there)
    re_path(r'^.*$', _react_index),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
