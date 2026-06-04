from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Vendor


class VendorRegisterTests(TestCase):
    def test_register_vendor_minimal(self):
        url = reverse('vendor-register')
        pdf = SimpleUploadedFile('test.pdf', b'PDFCONTENT', content_type='application/pdf')
        data = {
            'companyName': 'ACME Corp',
            'experienceDetails': 'We do stuff',
            'attendeeName': 'Alice',
            'bdeName': 'Bob',
            'meetingWith': 'Procurement',
            'qualification_status': 'qualified',
            'udyam_registration': 'yes',
            'gst_registration': 'no',
            'coi_registration': 'no',
            'moa_registration': 'no',
        }
        files = {'udyam_file': pdf}
        resp = self.client.post(url, data, files=files)
        self.assertEqual(resp.status_code, 200)
        json = resp.json()
        self.assertIn('vendor_code', json)
        self.assertTrue(Vendor.objects.filter(company_name='ACME Corp').exists())
