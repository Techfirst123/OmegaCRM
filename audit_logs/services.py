from audit_logs.models import VendorActivityLog


def log_vendor_activity(vendor, activity_type, description, performed_by=None):
    if not vendor:
        return None
    return VendorActivityLog.objects.create(
        vendor=vendor,
        activity_type=activity_type,
        performed_by=performed_by if getattr(performed_by, 'is_authenticated', False) else None,
        description=description,
    )

