from django.contrib import admin

from .models import (
    AppearanceSetting,
    BackupRecord,
    CompanySetting,
    DashboardSetting,
    EmailConfiguration,
    ERPConfiguration,
    HelpResource,
    LoginAttempt,
    MasterDataEntry,
    SecuritySetting,
    SupportTicket,
    SystemAuditLog,
    UserNotificationPreference,
    UserSessionRecord,
    WhatsAppConfiguration,
)


admin.site.register(CompanySetting)
admin.site.register(ERPConfiguration)
admin.site.register(SecuritySetting)
admin.site.register(EmailConfiguration)
admin.site.register(WhatsAppConfiguration)
admin.site.register(AppearanceSetting)
admin.site.register(DashboardSetting)
admin.site.register(MasterDataEntry)
admin.site.register(UserNotificationPreference)
admin.site.register(SystemAuditLog)
admin.site.register(UserSessionRecord)
admin.site.register(LoginAttempt)
admin.site.register(BackupRecord)
admin.site.register(SupportTicket)
admin.site.register(HelpResource)
