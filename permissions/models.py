from django.db import models

from .constants import ROLE_CHOICES


class RolePermission(models.Model):
    MODULE_VENDOR = 'vendors'
    MODULE_PURCHASE_ORDERS = 'purchase_orders'
    MODULE_DELIVERIES = 'deliveries'
    MODULE_INVENTORY = 'inventory'
    MODULE_PAYMENTS = 'payments'
    MODULE_PROJECTS = 'projects'
    MODULE_REPORTS = 'reports'
    MODULE_ACCOUNTS = 'accounts'
    MODULE_SETTINGS = 'settings'
    MODULE_CHOICES = [
        (MODULE_VENDOR, 'Vendors'),
        (MODULE_PURCHASE_ORDERS, 'Purchase Orders'),
        (MODULE_DELIVERIES, 'Deliveries'),
        (MODULE_INVENTORY, 'Inventory'),
        (MODULE_PAYMENTS, 'Payments'),
        (MODULE_PROJECTS, 'Projects'),
        (MODULE_REPORTS, 'Reports'),
        (MODULE_ACCOUNTS, 'Accounts'),
        (MODULE_SETTINGS, 'Settings & Administration'),
    ]

    role = models.CharField(max_length=40, choices=ROLE_CHOICES)
    module_key = models.CharField(max_length=40, choices=MODULE_CHOICES)
    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    can_assign = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'role_permissions'
        unique_together = ('role', 'module_key')
        ordering = ['role', 'module_key']

    def __str__(self):
        return f'{self.get_role_display()} - {self.get_module_key_display()}'
