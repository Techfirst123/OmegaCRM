from django.urls import path

from . import views


urlpatterns = [
    path('', views.administration_dashboard, name='administration-dashboard'),
    path('profile/', views.my_profile, name='administration-my-profile'),
    path('account-security/', views.account_security, name='administration-account-security'),
    path('notifications/', views.notification_settings_view, name='administration-notifications'),
    path('preferences/', views.preference_settings, name='administration-preferences'),
    path('company/', views.company_settings_view, name='administration-company-settings'),
    path('erp-configuration/', views.erp_configuration_view, name='administration-erp-configuration'),
    path('users-roles/', views.users_roles_view, name='administration-users-roles'),
    path('permissions/', views.permission_matrix_view, name='administration-permissions'),
    path('email/', views.email_settings_view, name='administration-email-settings'),
    path('whatsapp/', views.whatsapp_settings_view, name='administration-whatsapp-settings'),
    path('audit-logs/', views.audit_logs_view, name='administration-audit-logs'),
    path('backup-restore/', views.backup_restore_view, name='administration-backup-restore'),
    path('appearance/', views.appearance_settings_view, name='administration-appearance'),
    path('dashboard-settings/', views.dashboard_settings_view, name='administration-dashboard-settings'),
    path('security-settings/', views.security_settings_view, name='administration-security-settings'),
    path('system-health/', views.system_health_view, name='administration-system-health'),
    path('master-data/', views.master_data_view, name='administration-master-data'),
    path('help-support/', views.help_support_view, name='administration-help-support'),
    path('api/sessions/', views.sessions_api, name='administration-api-sessions'),
    path('api/audit/', views.audit_api, name='administration-api-audit'),
    path('api/master-data/', views.master_data_api, name='administration-api-master-data'),
]

