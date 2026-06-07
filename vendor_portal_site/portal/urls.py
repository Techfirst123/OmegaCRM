from django.urls import path

from . import views


urlpatterns = [
    path('', views.dashboard_view, name='portal-dashboard'),
    path('login/', views.login_view, name='portal-login'),
    path('logout/', views.logout_view, name='portal-logout'),
    path('forgot-password/', views.forgot_password_view, name='portal-forgot-password'),
    path('projects/', views.projects_view, name='portal-projects'),
    path('updates/', views.updates_view, name='portal-updates'),
    path('media/', views.media_view, name='portal-media'),
    path('documents/', views.documents_view, name='portal-documents'),
    path('issues/', views.issues_view, name='portal-issues'),
    path('notifications/', views.notifications_view, name='portal-notifications'),
    path('sessions/', views.sessions_view, name='portal-sessions'),
]
