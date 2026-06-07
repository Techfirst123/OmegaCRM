from django.contrib.auth.models import Group


ROLE_GROUPS = [
    'Admin',
    'Purchase Manager',
    'Accounts Team',
    'Project Manager',
    'Site Engineer',
    'Store Manager',
    'Vendor User',
]


def ensure_role_groups(sender, **kwargs):
    for group_name in ROLE_GROUPS:
        Group.objects.get_or_create(name=group_name)
