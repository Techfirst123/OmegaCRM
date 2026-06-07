from django.urls import path

from . import views

urlpatterns = [
    path('', views.report_center, name='procurement-reports'),
]
