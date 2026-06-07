from django.contrib.auth.models import Group


ROLE_GROUPS = [
    'Super Admin',
    'Admin',
    'HR',
    'Accounts',
    'Purchase Manager',
    'Vendor Manager',
    'Purchase Staff',
    'Accounts Staff',
    'Site Staff',
    'Site Engineer',
    'Project Manager',
    'Viewer',
    'Store Manager',
    'Vendor User',
]


def ensure_role_groups(sender, **kwargs):
    for group_name in ROLE_GROUPS:
        Group.objects.get_or_create(name=group_name)
