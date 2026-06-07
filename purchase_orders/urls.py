from django.urls import path

from . import views

urlpatterns = [
    path('', views.procurement_dashboard, name='procurement-dashboard'),
    path('purchase-orders/', views.purchase_order_master, name='purchase-order-master'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase-order-detail'),
    path('api/dashboard/', views.purchase_order_dashboard_api, name='purchase-order-dashboard-api'),
    path('api/purchase-orders/<int:pk>/', views.purchase_order_detail_api, name='purchase-order-detail-api'),
]
