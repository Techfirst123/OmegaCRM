from .models import VendorAssignment, VendorAssignmentHistory


def serialize_vendor_assignment(assignment: VendorAssignment):
    return {
        'id': assignment.id,
        'vendor_id': assignment.vendor.vendor_id,
        'vendor_name': assignment.vendor.company_name,
        'assigned_staff': assignment.assigned_staff.staff_name,
        'assignment_role': assignment.assignment_role,
        'status': assignment.assignment_status,
        'start_date': assignment.start_date.isoformat() if assignment.start_date else '',
        'end_date': assignment.end_date.isoformat() if assignment.end_date else '',
    }


def serialize_assignment_history(row: VendorAssignmentHistory):
    return {
        'id': row.id,
        'vendor_id': row.vendor.vendor_id,
        'vendor_name': row.vendor.company_name,
        'previous_staff': row.previous_staff.staff_name if row.previous_staff else '',
        'new_staff': row.new_staff.staff_name if row.new_staff else '',
        'changed_date': row.changed_date.isoformat(),
        'reason': row.reason,
    }

