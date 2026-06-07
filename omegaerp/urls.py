from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('administration/', include('administration.urls')),
    path('procurement/', include('purchase_orders.urls')),
    path('procurement/vendors/', include('vendors.urls')),
    path('procurement/reports/', include('reports.urls')),
    path('vendor-control/', include('vendors.management_urls')),
    path('vendor-portal/', include('vendor_portal.urls')),
    path('api/vendor-portal/', include('vendor_portal.api_urls')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

