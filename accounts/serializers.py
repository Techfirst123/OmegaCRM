from .models import StaffProfile


def serialize_staff_profile(profile: StaffProfile):
    return {
        'id': profile.id,
        'staff_name': profile.staff_name,
        'employee_id': profile.employee_id,
        'department': profile.department,
        'designation': profile.designation,
        'role': profile.role,
        'is_active': profile.is_active,
    }

