from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import StaffProfile
from core.models import ProjectMaster, ProjectWorkAllocation, Vendor, WorkPackage

from .forms import VendorPortalUserForm
from .models import VendorDailyUpdate, VendorProjectAssignment, VendorUser
from .services import recalculate_assignment_progress, sync_vendor_project_assignments


User = get_user_model()


class VendorPortalAccessTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='portaladmin',
            password='pass1234',
            is_staff=True,
        )
        StaffProfile.objects.create(
            user=self.admin_user,
            staff_name='Portal Admin',
            employee_id='ADM201',
            role='admin',
            is_active=True,
        )

        self.vendor = Vendor.objects.create(company_name='Portal Vendor One', vendor_name='Portal Vendor One')
        self.other_vendor = Vendor.objects.create(company_name='Portal Vendor Two', vendor_name='Portal Vendor Two')
        self.work_package = WorkPackage.objects.create(name='civil work', display_order=1)
        self.project = ProjectMaster.objects.create(
            project_name='Vendor Portal Project',
            client_name='MSDEC',
            procurement_source='EPC',
            business_unit='Omega EPC',
            project_location='Sangli, Maharashtra, India',
            total_mw=Decimal('25.00'),
            status='running',
        )
        self.other_project = ProjectMaster.objects.create(
            project_name='Hidden Project',
            client_name='Other Client',
            procurement_source='EPC',
            business_unit='Omega EPC',
            project_location='Kolhapur, Maharashtra, India',
            total_mw=Decimal('10.00'),
            status='running',
        )
        self.allocation = ProjectWorkAllocation.objects.create(
            project=self.project,
            work_package=self.work_package,
            vendor=self.vendor,
            allocated_mw=Decimal('10.00'),
            status='running',
        )
        ProjectWorkAllocation.objects.create(
            project=self.other_project,
            work_package=self.work_package,
            vendor=self.other_vendor,
            allocated_mw=Decimal('5.00'),
            status='running',
        )

        self.vendor_auth_user = User.objects.create_user(
            username='vendorlogin',
            password='pass1234',
            email='vendor@example.com',
        )
        self.vendor_portal_user = VendorUser.objects.create(
            user=self.vendor_auth_user,
            vendor=self.vendor,
            role=VendorUser.ROLE_VENDOR_ENGINEER,
            email='vendor@example.com',
            mobile_number='9999999999',
            is_active=True,
        )
        sync_vendor_project_assignments()

    def test_vendor_api_login_returns_token(self):
        response = self.client.post(
            reverse('vendor-portal-api-login'),
            {'identifier': 'vendorlogin', 'password': 'pass1234'},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['ok'])
        self.assertIn('token', payload)
        self.assertIn('token_expires_in', payload)

    def test_vendor_api_refresh_returns_new_token_payload(self):
        login_payload = self.client.post(
            reverse('vendor-portal-api-login'),
            {'identifier': 'vendorlogin', 'password': 'pass1234'},
        ).json()
        response = self.client.post(
            reverse('vendor-portal-api-refresh'),
            HTTP_AUTHORIZATION=f"Bearer {login_payload['token']}",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['ok'])
        self.assertIn('token', payload)
        self.assertIn('refresh_recommended_in', payload)

    def test_vendor_api_login_denied_without_active_assignment(self):
        self.allocation.delete()
        response = self.client.post(
            reverse('vendor-portal-api-login'),
            {'identifier': 'vendorlogin', 'password': 'pass1234'},
        )
        self.assertEqual(response.status_code, 403)
        payload = response.json()
        self.assertFalse(payload['ok'])
        self.assertIn('project assignment', payload['error'].lower())

    def test_vendor_api_projects_requires_token(self):
        response = self.client.get(reverse('vendor-portal-api-projects'))
        self.assertEqual(response.status_code, 401)

    def test_vendor_api_only_returns_own_projects(self):
        login_payload = self.client.post(
            reverse('vendor-portal-api-login'),
            {'identifier': 'vendorlogin', 'password': 'pass1234'},
        ).json()
        response = self.client.get(
            reverse('vendor-portal-api-projects'),
            HTTP_AUTHORIZATION=f"Bearer {login_payload['token']}",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        project_names = [row['project_name'] for row in payload['results']]
        self.assertIn('Vendor Portal Project', project_names)
        self.assertNotIn('Hidden Project', project_names)

    def test_vendor_api_token_blocked_when_assignment_removed(self):
        login_payload = self.client.post(
            reverse('vendor-portal-api-login'),
            {'identifier': 'vendorlogin', 'password': 'pass1234'},
        ).json()
        self.allocation.delete()
        response = self.client.get(
            reverse('vendor-portal-api-projects'),
            HTTP_AUTHORIZATION=f"Bearer {login_payload['token']}",
        )
        self.assertEqual(response.status_code, 403)
        payload = response.json()
        self.assertFalse(payload['ok'])
        self.assertIn('credential activation', payload['error'].lower())

    def test_vendor_portal_user_form_rejects_vendor_without_project_assignment(self):
        unassigned_vendor = Vendor.objects.create(company_name='No Assignment Vendor', vendor_name='No Assignment Vendor')
        form = VendorPortalUserForm(
            data={
                'vendor': unassigned_vendor.id,
                'username': 'noassignment',
                'password': 'Vendor@123',
                'email': 'noassignment@example.com',
                'mobile_number': '8888888888',
                'role': VendorUser.ROLE_VENDOR_OPERATOR,
                'is_active': True,
            },
            vendor_queryset=Vendor.objects.filter(id=unassigned_vendor.id),
        )
        self.assertFalse(form.is_valid())
        self.assertIn('Assign this vendor to at least one project', form.errors['vendor'][0])

    def test_recalculate_assignment_progress_updates_project_allocation(self):
        assignment = VendorProjectAssignment.objects.get(vendor_user=self.vendor_portal_user, project=self.project)
        daily_update = VendorDailyUpdate.objects.create(
            assignment=assignment,
            vendor_user=self.vendor_portal_user,
            work_category='Civil Work',
            work_description='Foundation work completed',
            quantity_completed=Decimal('4.00'),
            unit='MW',
            progress_percentage=Decimal('40.00'),
            status=VendorDailyUpdate.STATUS_APPROVED,
        )
        self.assertEqual(daily_update.status, VendorDailyUpdate.STATUS_APPROVED)
        recalculate_assignment_progress(assignment)

        self.allocation.refresh_from_db()
        self.assertEqual(self.allocation.completed_mw, Decimal('4.00'))
