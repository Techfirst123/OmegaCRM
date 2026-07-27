from django.urls import path

from tasks import views as task_views

from . import views


urlpatterns = [
    path('', views.vendor_authorization_dashboard, name='vendor-auth-dashboard'),
    path('staff/', views.staff_master, name='vendor-auth-staff-master'),
    path('assignments/', views.vendor_assignment_list, name='vendor-auth-assignments'),
    path('assignments/bulk/', views.vendor_bulk_assignment, name='vendor-auth-bulk-assignment'),
    path('distribution/', views.vendor_distribution, name='vendor-auth-distribution'),
    path('history/', views.vendor_assignment_history, name='vendor-auth-history'),
    path('tasks/', task_views.vendor_task_center, name='vendor-auth-tasks'),
    path('tasks/<int:task_id>/status/', task_views.update_task_status, name='vendor-auth-task-status'),
    path('followups/', task_views.my_followups, name='vendor-auth-followups'),
    path('performance/', views.staff_performance, name='vendor-auth-performance'),
    path('my-vendors/', views.my_vendors, name='vendor-auth-my-vendors'),
    path('vendors/<str:vendor_id>/', views.vendor_detail, name='vendor-auth-vendor-detail'),
    path('api/summary/', views.authorization_dashboard_api, name='vendor-auth-api-summary'),
    path('api/vendors/', views.accessible_vendors_api, name='vendor-auth-api-vendors'),
    path('api/assignments/', views.assignments_api, name='vendor-auth-api-assignments'),
    path('api/history/', views.assignment_history_api, name='vendor-auth-api-history'),
    path('api/tasks/', task_views.vendor_tasks_api, name='vendor-auth-api-tasks'),
]
