from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.api_login, name='api-auth-login'),
    path('logout/', views.api_logout, name='api-auth-logout'),
    path('session/', views.api_session, name='api-auth-session'),
]
