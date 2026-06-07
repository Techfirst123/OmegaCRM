from django.urls import path

from . import api_views


urlpatterns = [
    path('auth/login/', api_views.api_login, name='vendor-portal-api-login'),
    path('auth/logout/', api_views.api_logout, name='vendor-portal-api-logout'),
    path('auth/refresh/', api_views.api_refresh, name='vendor-portal-api-refresh'),
    path('dashboard/', api_views.api_dashboard, name='vendor-portal-api-dashboard'),
    path('projects/', api_views.api_projects, name='vendor-portal-api-projects'),
    path('updates/', api_views.api_updates, name='vendor-portal-api-updates'),
    path('media/', api_views.api_media, name='vendor-portal-api-media'),
    path('documents/', api_views.api_documents, name='vendor-portal-api-documents'),
    path('issues/', api_views.api_issues, name='vendor-portal-api-issues'),
    path('notifications/', api_views.api_notifications, name='vendor-portal-api-notifications'),
    path('sessions/', api_views.api_sessions, name='vendor-portal-api-sessions'),
]
