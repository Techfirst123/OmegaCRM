from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import StaffProfile
from administration.models import UserSessionRecord


User = get_user_model()


class AdministrationAccessTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='settingsadmin',
            password='pass1234',
            email='admin@example.com',
            is_staff=True,
        )
        self.staff_user = User.objects.create_user(
            username='settingsstaff',
            password='pass1234',
            email='staff@example.com',
        )

        self.admin_profile = StaffProfile.objects.create(
            user=self.admin_user,
            staff_name='Settings Admin',
            employee_id='ADM100',
            role='admin',
            is_active=True,
        )
        self.staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            staff_name='Settings Staff',
            employee_id='STF100',
            role='purchase_staff',
            is_active=True,
        )

    def test_admin_can_open_company_settings(self):
        self.client.login(username='settingsadmin', password='pass1234')
        response = self.client.get(reverse('administration-company-settings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Company Settings')

    def test_staff_is_blocked_from_company_settings(self):
        self.client.login(username='settingsstaff', password='pass1234')
        response = self.client.get(reverse('administration-company-settings'))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_open_personal_notifications(self):
        self.client.login(username='settingsstaff', password='pass1234')
        response = self.client.get(reverse('administration-notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Notification Channels')
        self.assertContains(response, 'Vendor Assigned')

    def test_sessions_api_returns_only_current_user_sessions(self):
        UserSessionRecord.objects.create(user=self.admin_user, session_key='admin-key', ip_address='10.0.0.1')
        UserSessionRecord.objects.create(user=self.staff_user, session_key='staff-key', ip_address='10.0.0.2')

        self.client.login(username='settingsstaff', password='pass1234')
        response = self.client.get(reverse('administration-api-sessions'))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        session_keys = [row['session_key'] for row in payload['results']]
        self.assertIn('staff-key', session_keys)
        self.assertNotIn('admin-key', session_keys)
