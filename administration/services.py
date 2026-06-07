import json
import tempfile

from django.core.management import call_command
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import (
    AppearanceSetting,
    BackupRecord,
    CompanySetting,
    DashboardSetting,
    EmailConfiguration,
    ERPConfiguration,
    SecuritySetting,
    SystemAuditLog,
    UserNotificationPreference,
    WhatsAppConfiguration,
    MasterDataEntry,
)
from permissions.models import RolePermission


DEFAULT_NOTIFICATION_EVENTS = {
    'vendor_assigned': True,
    'po_approved': True,
    'delivery_updated': True,
    'payment_approved': True,
    'task_assigned': True,
    'project_status_changed': True,
    'new_announcement': True,
}


def get_or_create_singleton(model_class):
    instance = model_class.objects.order_by('id').first()
    if instance:
        return instance
    return model_class.objects.create()


def get_company_setting():
    return get_or_create_singleton(CompanySetting)


def get_erp_configuration():
    return get_or_create_singleton(ERPConfiguration)


def get_security_setting():
    return get_or_create_singleton(SecuritySetting)


def get_email_configuration():
    return get_or_create_singleton(EmailConfiguration)


def get_whatsapp_configuration():
    return get_or_create_singleton(WhatsAppConfiguration)


def get_appearance_setting():
    return get_or_create_singleton(AppearanceSetting)


def get_dashboard_setting():
    return get_or_create_singleton(DashboardSetting)


def get_notification_preference(user):
    preference, _ = UserNotificationPreference.objects.get_or_create(
        user=user,
        defaults={'event_preferences_json': json.dumps(DEFAULT_NOTIFICATION_EVENTS)},
    )
    if not preference.event_preferences_json:
        preference.event_preferences_json = json.dumps(DEFAULT_NOTIFICATION_EVENTS)
        preference.save(update_fields=['event_preferences_json', 'updated_at'])
    return preference


def parse_json_field(raw_value, fallback):
    try:
        parsed = json.loads(raw_value or '')
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback
    return parsed


def log_system_audit(*, user=None, action=SystemAuditLog.ACTION_GENERIC, module='administration', description='', ip_address='', device_information='', metadata=None):
    return SystemAuditLog.objects.create(
        user=user if getattr(user, 'is_authenticated', False) else None,
        action=action,
        module=module,
        description=description,
        ip_address=ip_address,
        device_information=device_information,
        metadata_json=json.dumps(metadata or {}, default=str),
    )


class ListBuffer:
    def __init__(self):
        self.parts = []

    def write(self, value):
        self.parts.append(value)

    def __iter__(self):
        return iter(self.parts)

    def join(self):
        return ''.join(self.parts)


def create_backup_snapshot(*, user=None, note='Manual backup'):
    buffer = ListBuffer()
    call_command('dumpdata', stdout=buffer)
    backup = BackupRecord.objects.create(
        backup_type=BackupRecord.TYPE_MANUAL,
        note=note,
        created_by=user if getattr(user, 'is_authenticated', False) else None,
    )
    filename = f'backup-{timezone.now().strftime("%Y%m%d-%H%M%S")}.json'
    backup.file.save(filename, ContentFile(buffer.join()), save=True)
    return backup


def restore_backup_from_file(uploaded_file):
    uploaded_file.seek(0)
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name
    call_command('loaddata', temp_path)
    return temp_path


def ensure_role_permissions():
    default_modules = [choice[0] for choice in RolePermission.MODULE_CHOICES]
    for role, _label in RolePermission._meta.get_field('role').choices:
        for module_key in default_modules:
            permission, created = RolePermission.objects.get_or_create(
                role=role,
                module_key=module_key,
                defaults={
                    'can_view': role not in {'viewer'},
                    'can_create': role not in {'viewer'},
                    'can_edit': role not in {'viewer'},
                    'can_delete': role in {'super_admin', 'admin'},
                    'can_approve': role in {'super_admin', 'admin', 'purchase_manager', 'accounts', 'project_manager'},
                    'can_export': role in {'super_admin', 'admin', 'accounts', 'purchase_manager', 'viewer'},
                    'can_assign': role in {'super_admin', 'admin', 'vendor_manager'},
                },
            )
            if created:
                permission.save()


def seed_master_data_defaults():
    defaults = {
        MasterDataEntry.TYPE_VENDOR_CATEGORY: ['Service Provider', 'Sub-contractor'],
        MasterDataEntry.TYPE_MATERIAL_CATEGORY: ['Solar Panels', 'Inverters', 'Structures', 'Cables'],
        MasterDataEntry.TYPE_PROJECT_TYPE: ['Solar', 'Biogas', 'Infrastructure', 'Pharma'],
        MasterDataEntry.TYPE_DEPARTMENT: ['Purchase', 'Accounts', 'Projects', 'Sites', 'HR'],
        MasterDataEntry.TYPE_DESIGNATION: ['Manager', 'Executive', 'Engineer', 'Viewer'],
        MasterDataEntry.TYPE_LOCATION: ['Kolkata', 'Hazaribagh', 'Ranchi'],
        MasterDataEntry.TYPE_TAX_CATEGORY: ['GST 5%', 'GST 12%', 'GST 18%', 'GST 28%'],
        MasterDataEntry.TYPE_PAYMENT_MODE: ['NEFT', 'RTGS', 'UPI', 'Cheque', 'Cash'],
    }
    for master_type, names in defaults.items():
        for index, name in enumerate(names):
            MasterDataEntry.objects.get_or_create(
                master_type=master_type,
                name=name,
                defaults={'display_order': index},
            )
