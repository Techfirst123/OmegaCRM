from .models import MasterDataEntry, SystemAuditLog, UserSessionRecord


def serialize_audit_log(entry: SystemAuditLog):
    return {
        'id': entry.id,
        'user': entry.user.username if entry.user else '',
        'action': entry.action,
        'module': entry.module,
        'description': entry.description,
        'ip_address': entry.ip_address,
        'device_information': entry.device_information,
        'created_at': entry.created_at.isoformat(),
    }


def serialize_session_record(entry: UserSessionRecord):
    return {
        'id': entry.id,
        'user': entry.user.username,
        'session_key': entry.session_key,
        'ip_address': entry.ip_address,
        'is_active': entry.is_active,
        'logged_in_at': entry.logged_in_at.isoformat(),
        'last_activity_at': entry.last_activity_at.isoformat(),
    }


def serialize_master_data(entry: MasterDataEntry):
    return {
        'id': entry.id,
        'master_type': entry.master_type,
        'name': entry.name,
        'code': entry.code,
        'display_order': entry.display_order,
        'is_active': entry.is_active,
    }

