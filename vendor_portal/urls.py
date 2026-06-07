from django.urls import path

from . import views


urlpatterns = [
    path('login/', views.vendor_login, name='vendor-portal-login'),
    path('forgot-password/', views.vendor_forgot_password, name='vendor-portal-forgot-password'),
    path('reset-password/', views.vendor_reset_password, name='vendor-portal-reset-password'),
    path('logout/', views.vendor_logout, name='vendor-portal-logout'),
    path('', views.vendor_dashboard, name='vendor-portal-dashboard'),
    path('projects/', views.vendor_projects, name='vendor-portal-projects'),
    path('updates/', views.vendor_daily_updates, name='vendor-portal-updates'),
    path('media/', views.vendor_media_gallery, name='vendor-portal-media'),
    path('documents/', views.vendor_documents, name='vendor-portal-documents'),
    path('issues/', views.vendor_issues, name='vendor-portal-issues'),
    path('notifications/', views.vendor_notifications, name='vendor-portal-notifications'),
    path('sessions/', views.vendor_sessions, name='vendor-portal-sessions'),
]
