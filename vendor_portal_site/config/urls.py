from django.urls import include, path


urlpatterns = [
    path('', include('portal.urls')),
    path('vendor-portal/', include('portal.urls')),
]
