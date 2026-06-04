import json
import os

from django.core.management.base import BaseCommand

from vercel.blob import get

from core.models import BusinessUnit, MaterialMaster, Vendor, WorkPackage


def _clean_value(value):
    return '' if value is None else value


class Command(BaseCommand):
    help = 'Imports one-time legacy data from a private Vercel Blob JSON file when LEGACY_IMPORT_BLOB_PATH is set.'

    def handle(self, *args, **options):
        blob_path = os.environ.get('LEGACY_IMPORT_BLOB_PATH', '').strip()
        blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN', '').strip()

        if not blob_path:
            self.stdout.write('LEGACY_IMPORT_BLOB_PATH not set. Skipping legacy sync.')
            return

        if not blob_token:
            self.stdout.write('BLOB_READ_WRITE_TOKEN not set. Skipping legacy sync.')
            return

        blob = get(blob_path, access='private', token=blob_token)
        payload = json.loads(blob.content.decode('utf-8'))

        work_package_count = 0
        business_unit_count = 0
        vendor_count = 0
        material_count = 0

        for item in payload.get('work_packages', []):
            defaults = {
                'display_order': item.get('display_order', 0),
                'is_active': item.get('is_active', True),
            }
            WorkPackage.objects.update_or_create(name=item['name'], defaults=defaults)
            work_package_count += 1

        for item in payload.get('business_units', []):
            defaults = {
                'display_order': item.get('display_order', 0),
                'is_active': item.get('is_active', True),
            }
            BusinessUnit.objects.update_or_create(name=item['name'], defaults=defaults)
            business_unit_count += 1

        vendor_fields = [
            'company_name', 'experience_details', 'address', 'address2', 'city', 'state', 'pin_code', 'country',
            'vendor_type', 'vendor_category', 'contact_person', 'email_id', 'attendee_name', 'bde_name',
            'meeting_with', 'qualification_status', 'msme_reg', 'pan_no', 'pf_reg', 'gst_no', 'gst_type',
            'gst_status', 'last_gstr1', 'gst_pending_status', 'aadhaar_no', 'labour_welfare_fund',
            'professional_tax', 'turnover_year_1', 'turnover_year_2', 'turnover_year_3', 'bank_account_name',
            'bank_name_address', 'account_type', 'account_number', 'bank_proof_type', 'passbook_file',
            'client_list_data',
        ]
        for item in payload.get('vendors', []):
            defaults = {field: _clean_value(item.get(field, '')) for field in vendor_fields}
            vendor_key = item.get('vendor_id') or item.get('company_name')
            Vendor.objects.update_or_create(vendor_id=vendor_key, defaults=defaults)
            vendor_count += 1

        material_fields = [
            'work_package', 'material_name', 'specification', 'qty', 'qty_specification', 'no_of_site', 'mw',
            'lt_panel', 'lt_panels', 'pf_rate', 'amount',
        ]
        for item in payload.get('materials', []):
            defaults = {field: item.get(field) for field in material_fields}
            material_code = item.get('material_code') or ''
            lookup = {'material_code': material_code} if material_code else {
                'material_name': item.get('material_name', ''),
                'specification': item.get('specification', ''),
            }
            MaterialMaster.objects.update_or_create(**lookup, defaults=defaults)
            material_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Legacy sync complete: {work_package_count} work packages, '
                f'{business_unit_count} business units, {vendor_count} vendors, '
                f'{material_count} materials.'
            )
        )
