from django.urls import path

from . import views

urlpatterns = [
    path('', views.vendor_master, name='procurement-vendor-master'),
]
