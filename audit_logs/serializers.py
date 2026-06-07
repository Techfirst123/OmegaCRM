from .models import VendorActivityLog


def serialize_vendor_activity(entry: VendorActivityLog):
    return {
        'id': entry.id,
        'vendor_id': entry.vendor.vendor_id,
        'activity_type': entry.activity_type,
        'description': entry.description,
        'performed_by': entry.performed_by.username if entry.performed_by else '',
        'created_at': entry.created_at.isoformat(),
    }

