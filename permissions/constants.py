ROLE_SUPER_ADMIN = 'super_admin'
ROLE_ADMIN = 'admin'
ROLE_HR = 'hr'
ROLE_ACCOUNTS = 'accounts'
ROLE_PURCHASE_MANAGER = 'purchase_manager'
ROLE_VENDOR_MANAGER = 'vendor_manager'
ROLE_PURCHASE_STAFF = 'purchase_staff'
ROLE_ACCOUNTS_STAFF = 'accounts_staff'
ROLE_SITE_STAFF = 'site_staff'
ROLE_SITE_ENGINEER = 'site_engineer'
ROLE_PROJECT_MANAGER = 'project_manager'
ROLE_VIEWER = 'viewer'

ROLE_CHOICES = [
    (ROLE_SUPER_ADMIN, 'Super Admin'),
    (ROLE_ADMIN, 'Admin'),
    (ROLE_HR, 'HR'),
    (ROLE_ACCOUNTS, 'Accounts'),
    (ROLE_PURCHASE_MANAGER, 'Purchase Manager'),
    (ROLE_VENDOR_MANAGER, 'Vendor Manager'),
    (ROLE_PURCHASE_STAFF, 'Purchase Staff'),
    (ROLE_ACCOUNTS_STAFF, 'Accounts Staff'),
    (ROLE_SITE_STAFF, 'Site Staff'),
    (ROLE_SITE_ENGINEER, 'Site Engineer'),
    (ROLE_PROJECT_MANAGER, 'Project Manager'),
    (ROLE_VIEWER, 'Viewer'),
]

ROLE_GROUP_MAP = {
    ROLE_SUPER_ADMIN: 'Super Admin',
    ROLE_ADMIN: 'Admin',
    ROLE_HR: 'HR',
    ROLE_ACCOUNTS: 'Accounts',
    ROLE_PURCHASE_MANAGER: 'Purchase Manager',
    ROLE_VENDOR_MANAGER: 'Vendor Manager',
    ROLE_PURCHASE_STAFF: 'Purchase Staff',
    ROLE_ACCOUNTS_STAFF: 'Accounts Staff',
    ROLE_SITE_STAFF: 'Site Staff',
    ROLE_SITE_ENGINEER: 'Site Engineer',
    ROLE_PROJECT_MANAGER: 'Project Manager',
    ROLE_VIEWER: 'Viewer',
}

ADMIN_LIKE_ROLES = {ROLE_SUPER_ADMIN, ROLE_ADMIN}
STAFF_ROLES = {
    ROLE_HR,
    ROLE_ACCOUNTS,
    ROLE_PURCHASE_MANAGER,
    ROLE_VENDOR_MANAGER,
    ROLE_PURCHASE_STAFF,
    ROLE_ACCOUNTS_STAFF,
    ROLE_SITE_STAFF,
    ROLE_SITE_ENGINEER,
    ROLE_PROJECT_MANAGER,
}

READ_ONLY_ROLES = {ROLE_VIEWER}
