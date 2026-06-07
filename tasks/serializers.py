from .models import VendorTask


def serialize_vendor_task(task: VendorTask):
    return {
        'id': task.id,
        'vendor_id': task.vendor.vendor_id,
        'vendor_name': task.vendor.company_name,
        'assigned_staff': task.assigned_staff.staff_name,
        'task_title': task.task_title,
        'task_type': task.task_type,
        'priority': task.priority,
        'due_date': task.due_date.isoformat(),
        'task_status': task.task_status,
    }

