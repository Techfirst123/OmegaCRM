from django.urls import path

from . import views


urlpatterns = [
    path('', views.vendor_portal_management_dashboard, name='vendor-portal-admin-dashboard'),
    path('users/', views.vendor_portal_user_management, name='vendor-portal-user-management'),
    path('reviews/', views.vendor_portal_review_queue, name='vendor-portal-review-queue'),
    path('reviews/<int:update_id>/', views.vendor_portal_review_detail, name='vendor-portal-review-detail'),
    path('api/dashboard/', views.vendor_portal_dashboard_api, name='vendor-portal-dashboard-api'),
]
