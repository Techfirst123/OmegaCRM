from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import StaffProfile
from core.models import Vendor
from tasks.models import VendorTask
from vendors.models import VendorAssignment


User = get_user_model()


class VendorAuthorizationAccessTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='adminuser', password='pass1234', is_staff=True)
        self.staff_user = User.objects.create_user(username='staffuser', password='pass1234')
        self.other_user = User.objects.create_user(username='otheruser', password='pass1234')

        self.admin_profile = StaffProfile.objects.create(
            user=self.admin_user,
            staff_name='Admin User',
            employee_id='EMP001',
            role='admin',
            is_active=True,
        )
        self.staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            staff_name='Staff User',
            employee_id='EMP002',
            role='purchase_staff',
            is_active=True,
        )
        self.other_profile = StaffProfile.objects.create(
            user=self.other_user,
            staff_name='Other User',
            employee_id='EMP003',
            role='site_staff',
            is_active=True,
        )

        self.vendor_one = Vendor.objects.create(company_name='Assigned Vendor', vendor_name='Assigned Vendor')
        self.vendor_two = Vendor.objects.create(company_name='Hidden Vendor', vendor_name='Hidden Vendor')

        VendorAssignment.objects.create(
            vendor=self.vendor_one,
            assigned_staff=self.staff_profile,
            assigned_by=self.admin_user,
            assignment_role=VendorAssignment.ROLE_PRIMARY,
            assignment_status=VendorAssignment.STATUS_ACTIVE,
        )
        VendorAssignment.objects.create(
            vendor=self.vendor_two,
            assigned_staff=self.other_profile,
            assigned_by=self.admin_user,
            assignment_role=VendorAssignment.ROLE_PRIMARY,
            assignment_status=VendorAssignment.STATUS_ACTIVE,
        )

        VendorTask.objects.create(
            vendor=self.vendor_one,
            assigned_staff=self.staff_profile,
            task_title='Collect GST',
            task_type=VendorTask.TYPE_DOCUMENT_COLLECTION,
            priority=VendorTask.PRIORITY_HIGH,
            due_date=timezone.localdate(),
            created_by=self.admin_user,
        )
        VendorTask.objects.create(
            vendor=self.vendor_two,
            assigned_staff=self.other_profile,
            task_title='Hidden task',
            task_type=VendorTask.TYPE_GENERAL,
            priority=VendorTask.PRIORITY_LOW,
            due_date=timezone.localdate(),
            created_by=self.admin_user,
        )

    def test_admin_sees_all_vendors_in_control_list(self):
        self.client.login(username='adminuser', password='pass1234')
        response = self.client.get(reverse('vendor-auth-my-vendors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Assigned Vendor')
        self.assertContains(response, 'Hidden Vendor')

    def test_staff_only_sees_assigned_vendor(self):
        self.client.login(username='staffuser', password='pass1234')
        response = self.client.get(reverse('vendor-auth-my-vendors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Assigned Vendor')
        self.assertNotContains(response, 'Hidden Vendor')

    def test_staff_gets_403_for_unassigned_vendor_detail(self):
        self.client.login(username='staffuser', password='pass1234')
        response = self.client.get(reverse('vendor-auth-vendor-detail', kwargs={'vendor_id': self.vendor_two.vendor_id}))
        self.assertEqual(response.status_code, 403)

    def test_staff_task_center_hides_other_vendor_tasks(self):
        self.client.login(username='staffuser', password='pass1234')
        response = self.client.get(reverse('vendor-auth-tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Collect GST')
        self.assertNotContains(response, 'Hidden task')
