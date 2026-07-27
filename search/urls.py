from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_view, name='search'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/chat/', views.api_chat, name='api_chat'),
]
