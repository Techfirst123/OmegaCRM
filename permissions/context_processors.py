from .models import RolePermission
from .utils import get_user_role, is_admin_like, is_view_only, role_label

_ALL_MODULES = [
    'vendors', 'purchase_orders', 'deliveries', 'inventory',
    'payments', 'projects', 'reports', 'accounts', 'settings',
]

_FULL_PERM = {
    'can_view': True, 'can_create': True, 'can_edit': True,
    'can_delete': True, 'can_approve': True, 'can_export': True, 'can_assign': True,
}


def user_permissions_context(request):
    user = request.user
    if not getattr(user, 'is_authenticated', False):
        return {
            'user_role': None,
            'user_role_label': 'Guest',
            'is_admin': False,
            'is_viewer': False,
            'user_perms': {},
        }

    role = get_user_role(user)
    admin = is_admin_like(user)

    if admin:
        perms = {m: dict(_FULL_PERM) for m in _ALL_MODULES}
    elif role:
        perm_qs = RolePermission.objects.filter(role=role)
        perms = {
            p.module_key: {
                'can_view': p.can_view,
                'can_create': p.can_create,
                'can_edit': p.can_edit,
                'can_delete': p.can_delete,
                'can_approve': p.can_approve,
                'can_export': p.can_export,
                'can_assign': p.can_assign,
            }
            for p in perm_qs
        }
    else:
        perms = {}

    return {
        'user_role': role,
        'user_role_label': role_label(user),
        'is_admin': admin,
        'is_viewer': is_view_only(user),
        'user_perms': perms,
    }
