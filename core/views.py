import json
import re
import traceback
import zipfile
from decimal import Decimal, InvalidOperation
from io import BytesIO
from xml.etree import ElementTree as ET

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .material_catalog import DEFAULT_BUSINESS_UNITS, DEFAULT_WORK_PACKAGES, MATERIAL_IMPORT_SCHEMA
from .models import (
    BusinessUnit,
    MaterialMaster,
    MaterialQuotation,
    ProjectMaster,
    ProjectPlanner,
    ProjectWorkAllocation,
    Vendor,
    WorkPackage,
)


def _normalize_material_header(value):
    return re.sub(r'[^a-z0-9]+', '', str(value or '').lower())


def _material_import_header_map():
    aliases = {
        'materialcode': 'material_code',
        'materialname': 'material_name',
        'specification': 'specification',
        'qty': 'qty',
        'qtyspecification': 'qty_specification',
        'noofsite': 'no_of_site',
        'mw': 'mw',
        'ltpanel': 'lt_panel',
        'ltpanels': 'lt_panels',
        'pfrate': 'pf_rate',
        'amount': 'amount',
    }
    return aliases


def _xlsx_column_to_index(column_ref):
    index = 0
    for char in column_ref:
        if char.isalpha():
            index = (index * 26) + (ord(char.upper()) - ord('A') + 1)
    return max(index - 1, 0)


def _load_xlsx_rows(uploaded_file):
    uploaded_file.seek(0)
    file_bytes = uploaded_file.read()
    archive = zipfile.ZipFile(BytesIO(file_bytes))

    workbook_tree = ET.fromstring(archive.read('xl/workbook.xml'))
    workbook_rels_tree = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
    ns_main = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    ns_rel = {'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    ns_pkg = {'pkg': 'http://schemas.openxmlformats.org/package/2006/relationships'}

    sheets = workbook_tree.find('main:sheets', ns_main)
    if sheets is None or not list(sheets):
        return []

    first_sheet = list(sheets)[0]
    relationship_id = first_sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    rel_targets = {
        rel.attrib.get('Id'): rel.attrib.get('Target')
        for rel in workbook_rels_tree.findall('pkg:Relationship', ns_pkg)
    }
    sheet_target = rel_targets.get(relationship_id, 'worksheets/sheet1.xml')
    sheet_path = f"xl/{sheet_target.lstrip('/')}" if not sheet_target.startswith('xl/') else sheet_target

    shared_strings = []
    if 'xl/sharedStrings.xml' in archive.namelist():
        shared_tree = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        for string_item in shared_tree.findall('main:si', ns_main):
            parts = [node.text or '' for node in string_item.findall('.//main:t', ns_main)]
            shared_strings.append(''.join(parts))

    sheet_tree = ET.fromstring(archive.read(sheet_path))
    rows = []
    for row_node in sheet_tree.findall('.//main:sheetData/main:row', ns_main):
        cells = {}
        max_index = -1
        for cell in row_node.findall('main:c', ns_main):
            cell_ref = cell.attrib.get('r', '')
            col_ref = ''.join(char for char in cell_ref if char.isalpha())
            col_index = _xlsx_column_to_index(col_ref)
            max_index = max(max_index, col_index)
            cell_type = cell.attrib.get('t')
            if cell_type == 'inlineStr':
                value = ''.join(node.text or '' for node in cell.findall('.//main:t', ns_main))
            else:
                value_node = cell.find('main:v', ns_main)
                raw_value = value_node.text if value_node is not None else ''
                if cell_type == 's':
                    try:
                        value = shared_strings[int(raw_value)]
                    except (ValueError, IndexError):
                        value = raw_value
                else:
                    value = raw_value
            cells[col_index] = value
        if max_index >= 0:
            rows.append([cells.get(index, '') for index in range(max_index + 1)])
    return rows


def _build_material_import_rows(raw_rows):
    rows = []
    for raw_row in raw_rows:
        row_values = []
        for key, _label in MATERIAL_IMPORT_SCHEMA:
            row_values.append(raw_row.get(key, ''))
        rows.append(row_values)
    return rows


def _default_material_import_rows():
    return []


def _material_code_for_index(index):
    sequence = max(int(index), 1)
    width = max(2, len(str(sequence)))
    return f"MAT{sequence:0{width}d}"


def _to_decimal_or_none(value):
    text = str(value or '').strip().replace(',', '')
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _to_int_or_none(value):
    text = str(value or '').strip().replace(',', '')
    if not text:
        return None
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError):
        return None
    if parsed != parsed.to_integral_value():
        return None
    return int(parsed)


def _serialize_material_rows(queryset):
    rows = []
    for index, item in enumerate(queryset, start=1):
        rows.append({
            'id': item.id,
            'material_code': item.material_code or _material_code_for_index(index),
            'work_package': item.work_package or '',
            'material_name': item.material_name or '',
            'specification': item.specification or '',
            'qty': '' if item.qty is None else str(item.qty),
            'qty_specification': item.qty_specification or '',
            'no_of_site': item.no_of_site or '',
            'mw': '' if item.mw is None else str(item.mw),
            'lt_panel': item.lt_panel or '',
            'lt_panels': item.lt_panels or '',
            'pf_rate': '' if item.pf_rate is None else str(item.pf_rate),
            'amount': '' if item.amount is None else str(item.amount),
        })
    return rows


def _group_material_rows(material_rows):
    grouped_rows = []
    grouped_lookup = {}

    for row in material_rows:
        material_name = (row.get('material_name') or '').strip() or 'Unspecified Material'
        group_key = material_name.lower()
        if group_key not in grouped_lookup:
            group = {
                'key': group_key,
                'material_name': material_name,
                'row_count': 0,
                'rows': [],
            }
            grouped_lookup[group_key] = group
            grouped_rows.append(group)

        grouped_lookup[group_key]['rows'].append(row)
        grouped_lookup[group_key]['row_count'] += 1

    return grouped_rows


def _get_work_package_names():
    work_packages = list(
        WorkPackage.objects.filter(is_active=True).order_by('display_order', 'id').values_list('name', flat=True)
    )
    return work_packages or list(DEFAULT_WORK_PACKAGES)


def _get_business_unit_names():
    business_units = list(
        BusinessUnit.objects.filter(is_active=True).order_by('display_order', 'id').values_list('name', flat=True)
    )
    return business_units or list(DEFAULT_BUSINESS_UNITS)


def _serialize_project_rows(queryset):
    rows = []
    for project in queryset:
        rows.append({
            'id': project.id,
            'project_code': project.project_code or '',
            'project_name': project.project_name or '',
            'client_name': project.client_name or '',
            'procurement_source': project.procurement_source or '',
            'business_unit': project.business_unit or '',
            'project_location': project.project_location or '',
            'total_mw': '' if project.total_mw is None else str(project.total_mw),
            'status': project.status or '',
            'note': project.note or '',
            'created_at': project.created_at.strftime('%d %b %Y') if project.created_at else '',
        })
    return rows


def _serialize_project_allocations(project):
    rows = []
    for allocation in project.allocations.select_related('vendor', 'work_package').order_by('id'):
        rows.append({
            'id': allocation.id,
            'work_package': allocation.work_package.name if allocation.work_package else '',
            'vendor_id': allocation.vendor.vendor_id if allocation.vendor else '',
            'vendor_name': allocation.vendor.company_name if allocation.vendor else '',
            'allocated_mw': '' if allocation.allocated_mw is None else str(allocation.allocated_mw),
            'status': allocation.status or '',
            'scope_note': allocation.scope_note or '',
        })
    return rows


def index(request):
    vendors = list(Vendor.objects.order_by('-created_at'))
    vendor_count = len(vendors)
    qualified_count = sum(1 for vendor in vendors if vendor.qualification_status == 'qualified')
    disqualified_count = sum(1 for vendor in vendors if vendor.qualification_status == 'disqualified')
    other_count = max(vendor_count - qualified_count - disqualified_count, 0)
    category_counts = {
        'service-provider': sum(1 for vendor in vendors if vendor.vendor_category == 'service-provider'),
        'sub-contractor': sum(1 for vendor in vendors if vendor.vendor_category == 'sub-contractor'),
    }
    context = {
        'page_title': 'Dashboard',
        'vendor_count': vendor_count,
        'qualified_count': qualified_count,
        'disqualified_count': disqualified_count,
        'other_count': other_count,
        'status_chart_data': json.dumps([qualified_count, disqualified_count, other_count]),
        'category_chart_data': json.dumps([category_counts['service-provider'], category_counts['sub-contractor']]),
    }
    return render(request, 'dashboard.html', context)


def vendor_module(request):
    vendor_count = Vendor.objects.count()
    recent_count = Vendor.objects.order_by('-created_at')[:5].count()
    context = {
        'page_title': 'Vendor Module',
        'vendor_module_nav': True,
        'vendor_count': vendor_count,
        'recent_count': recent_count,
    }
    return render(request, 'vendor_module.html', context)


def project_module(request):
    project_count = ProjectMaster.objects.count()
    active_count = ProjectMaster.objects.filter(status='active').count()
    allocation_count = ProjectWorkAllocation.objects.count()
    total_capacity = sum(
        [project.total_mw or Decimal('0') for project in ProjectMaster.objects.all()],
        Decimal('0')
    )
    context = {
        'page_title': 'Project Module',
        'project_module_nav': True,
        'project_count': project_count,
        'active_count': active_count,
        'allocation_count': allocation_count,
        'total_capacity': total_capacity,
        'business_unit_count': BusinessUnit.objects.filter(is_active=True).count(),
    }
    return render(request, 'project_module.html', context)


def project_master(request):
    projects = ProjectMaster.objects.order_by('-created_at')
    context = {
        'page_title': 'Project Master',
        'project_module_nav': True,
        'projects': _serialize_project_rows(projects),
        'project_count': projects.count(),
        'business_units': _get_business_unit_names(),
    }
    return render(request, 'project_master.html', context)


def project_distribution(request):
    projects = ProjectMaster.objects.order_by('-created_at')
    selected_project = projects.first()
    vendors = list(
        Vendor.objects.order_by('company_name').values('vendor_id', 'company_name', 'vendor_category')
    )
    work_packages = list(
        WorkPackage.objects.filter(is_active=True).order_by('display_order', 'id').values('id', 'name')
    )
    allocation_map = {
        str(project.id): _serialize_project_allocations(project)
        for project in projects
    }
    context = {
        'page_title': 'Vendor Distribution',
        'project_module_nav': True,
        'projects': _serialize_project_rows(projects),
        'selected_project': selected_project,
        'selected_allocations': _serialize_project_allocations(selected_project) if selected_project else [],
        'allocation_map': allocation_map,
        'vendor_options': vendors,
        'work_packages': work_packages,
        'business_units': _get_business_unit_names(),
    }
    return render(request, 'project_distribution.html', context)


def vendor_list(request):
    vendors = Vendor.objects.order_by('-created_at')
    context = {
        'page_title': 'Vendor List',
        'vendor_module_nav': True,
        'vendors': vendors,
    }
    return render(request, 'vendor_list.html', context)


def vendor_registration(request):
    return render(request, 'vendor_registration.html', {'page_title': 'Vendor Registration', 'vendor_module_nav': True})


def vendor_planner(request):
    vendors = list(
        Vendor.objects.order_by('company_name').values('vendor_id', 'company_name', 'vendor_category')
    )
    material_rows = _serialize_material_rows(MaterialMaster.objects.order_by('id'))
    work_packages = _get_work_package_names()
    context = {
        'page_title': 'Planner Prototype',
        'material_module_nav': True,
        'vendor_options': vendors,
        'materials': material_rows,
        'work_packages': work_packages,
        'planner_count': ProjectPlanner.objects.count(),
    }
    return render(request, 'vendor_planner.html', context)


def material_module(request):
    material_count = MaterialMaster.objects.count()
    work_type_count = WorkPackage.objects.filter(is_active=True).count()
    unique_units = sorted({item.qty_specification for item in MaterialMaster.objects.exclude(qty_specification='')})
    context = {
        'page_title': 'Material Master',
        'material_module_nav': True,
        'material_count': material_count,
        'work_type_count': work_type_count,
        'unit_count': len(unique_units),
        'quotation_count': MaterialQuotation.objects.count(),
        'planner_count': ProjectPlanner.objects.count(),
    }
    return render(request, 'material_module.html', context)


@ensure_csrf_cookie
def material_master(request):
    material_rows = _serialize_material_rows(MaterialMaster.objects.order_by('id'))
    work_packages = _get_work_package_names()
    context = {
        'page_title': 'Material Master',
        'material_module_nav': True,
        'material_import_columns': [label for _key, label in MATERIAL_IMPORT_SCHEMA],
        'work_types': work_packages,
        'material_rows': material_rows,
        'material_groups': _group_material_rows(material_rows),
        'imported_material_rows': _build_material_import_rows(material_rows),
        'imported_material_count': len(material_rows),
    }
    return render(request, 'material_master.html', context)


def material_quotation(request):
    vendors = list(
        Vendor.objects.order_by('company_name').values('vendor_id', 'company_name', 'vendor_category')
    )
    materials = _serialize_material_rows(MaterialMaster.objects.order_by('id'))
    work_packages = _get_work_package_names()
    context = {
        'page_title': 'Material Quotation Generator',
        'material_module_nav': True,
        'materials': materials,
        'work_types': work_packages,
        'vendor_options': vendors,
        'business_units': _get_business_unit_names(),
    }
    return render(request, 'material_quotation.html', context)


def import_material_master(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    headers = []
    rows = []

    if 'materialFile' in request.FILES:
        uploaded_file = request.FILES['materialFile']
        filename = (uploaded_file.name or '').lower()
        if not filename.endswith('.xlsx'):
            return JsonResponse({'error': 'Please upload the material list in .xlsx format'}, status=400)
        try:
            xlsx_rows = _load_xlsx_rows(uploaded_file)
        except (KeyError, zipfile.BadZipFile, ET.ParseError):
            return JsonResponse({'error': 'Could not read the Excel file. Please upload a valid .xlsx file'}, status=400)
        if not xlsx_rows:
            return JsonResponse({'error': 'The uploaded Excel sheet is empty'}, status=400)
        headers = xlsx_rows[0]
        rows = [row for row in xlsx_rows[1:] if any(str(cell or '').strip() for cell in row)]
    else:
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
        headers = payload.get('headers') or []
        rows = payload.get('rows') or []

    if not headers:
        return JsonResponse({'error': 'Excel header row is required'}, status=400)
    if not rows:
        return JsonResponse({'error': 'Excel data rows are required'}, status=400)

    header_aliases = _material_import_header_map()
    normalized_headers = [_normalize_material_header(header) for header in headers]
    header_keys = []
    for header in normalized_headers:
        key = header_aliases.get(header)
        if not key:
            return JsonResponse({'error': f'Unexpected column found: {header or "blank"}'}, status=400)
        header_keys.append(key)

    required_keys = [key for key, _label in MATERIAL_IMPORT_SCHEMA]
    missing_keys = [label for key, label in MATERIAL_IMPORT_SCHEMA if key not in header_keys]
    if missing_keys:
        return JsonResponse({'error': f'Missing required columns: {", ".join(missing_keys)}'}, status=400)

    imported_rows = []
    for row_number, raw_row in enumerate(rows, start=2):
        row_dict = {key: '' for key in required_keys}
        for index, key in enumerate(header_keys):
            value = raw_row[index] if index < len(raw_row) else ''
            row_dict[key] = '' if value is None else str(value).strip()
        if any(str(value).strip() for value in row_dict.values()):
            if _to_int_or_none(row_dict['qty']) is None:
                return JsonResponse({'error': f'Qty must be an integer value in Excel row {row_number}'}, status=400)
            imported_rows.append(row_dict)

    if not imported_rows:
        return JsonResponse({'error': 'No non-empty material rows found in the uploaded file'}, status=400)

    MaterialMaster.objects.all().delete()
    MaterialMaster.objects.bulk_create([
        MaterialMaster(
            material_code=_material_code_for_index(index),
            work_package='',
            material_name=row['material_name'],
            specification=row['specification'],
            qty=_to_int_or_none(row['qty']),
            qty_specification=row['qty_specification'],
            no_of_site=row['no_of_site'],
            mw=_to_decimal_or_none(row['mw']),
            lt_panel=row['lt_panel'],
            lt_panels=row['lt_panels'],
            pf_rate=_to_decimal_or_none(row['pf_rate']),
            amount=_to_decimal_or_none(row['amount']),
        )
        for index, row in enumerate(imported_rows, start=1)
    ])
    return JsonResponse({'message': 'Material list imported successfully', 'row_count': len(imported_rows)})


def clear_material_import(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    MaterialMaster.objects.all().delete()
    return JsonResponse({'message': 'Imported material list cleared'})


def update_material_work_package(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    material_id = payload.get('materialId')
    work_package = (payload.get('workPackage') or '').strip()

    if not material_id:
        return JsonResponse({'error': 'materialId is required'}, status=400)
    if work_package and work_package not in _get_work_package_names():
        return JsonResponse({'error': 'Invalid work package selected'}, status=400)

    try:
        material = MaterialMaster.objects.get(id=material_id)
    except MaterialMaster.DoesNotExist:
        return JsonResponse({'error': 'Material record not found'}, status=404)

    material.work_package = work_package
    material.save(update_fields=['work_package'])
    return JsonResponse({'message': 'Work package updated successfully'})


def create_project_master(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    project_name = (payload.get('projectName') or '').strip()
    client_name = (payload.get('clientName') or '').strip()
    procurement_source = (payload.get('procurementSource') or '').strip()
    business_unit = (payload.get('businessUnit') or '').strip()
    project_location = (payload.get('projectLocation') or '').strip()
    total_mw = _to_decimal_or_none(payload.get('totalMw'))
    status = (payload.get('status') or '').strip()
    note = (payload.get('note') or '').strip()

    errors = []
    if not project_name:
        errors.append('projectName is required')
    if not procurement_source:
        errors.append('procurementSource is required')
    if not business_unit:
        errors.append('businessUnit is required')
    elif business_unit not in _get_business_unit_names():
        errors.append('businessUnit is invalid')
    if total_mw is None or total_mw <= 0:
        errors.append('totalMw must be greater than zero')
    if not status:
        errors.append('status is required')
    if errors:
        return JsonResponse({'error': errors}, status=400)

    project = ProjectMaster.objects.create(
        project_name=project_name,
        client_name=client_name,
        procurement_source=procurement_source,
        business_unit=business_unit,
        project_location=project_location,
        total_mw=total_mw,
        status=status,
        note=note,
    )
    return JsonResponse({
        'message': 'Project master created successfully',
        'project': {
            'id': project.id,
            'project_code': project.project_code,
            'project_name': project.project_name,
            'client_name': project.client_name,
            'procurement_source': project.procurement_source,
            'business_unit': project.business_unit,
            'project_location': project.project_location,
            'total_mw': str(project.total_mw or ''),
            'status': project.status,
            'note': project.note,
            'created_at': project.created_at.strftime('%d %b %Y'),
        }
    })


def save_project_distribution(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    project_id = payload.get('projectId')
    allocation_rows = payload.get('allocations') or []

    if not project_id:
        return JsonResponse({'error': 'projectId is required'}, status=400)
    try:
        project = ProjectMaster.objects.get(id=project_id)
    except ProjectMaster.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

    work_package_ids = {str(item['id']): item['id'] for item in WorkPackage.objects.filter(is_active=True).values('id')}
    vendor_lookup = {
        vendor['vendor_id']: vendor['id']
        for vendor in Vendor.objects.values('id', 'vendor_id')
    }

    cleaned_rows = []
    total_allocated = Decimal('0')
    for index, row in enumerate(allocation_rows, start=1):
        work_package_id = str(row.get('workPackageId') or '').strip()
        vendor_id = (row.get('vendorId') or '').strip()
        allocated_mw = _to_decimal_or_none(row.get('allocatedMw'))
        status = (row.get('status') or '').strip()
        scope_note = (row.get('scopeNote') or '').strip()

        if not work_package_id or work_package_id not in work_package_ids:
            return JsonResponse({'error': f'Valid work package is required in row {index}'}, status=400)
        if not vendor_id or vendor_id not in vendor_lookup:
            return JsonResponse({'error': f'Valid vendor is required in row {index}'}, status=400)
        if allocated_mw is None or allocated_mw <= 0:
            return JsonResponse({'error': f'Allocated MW must be greater than zero in row {index}'}, status=400)

        total_allocated += allocated_mw
        cleaned_rows.append({
            'work_package_id': work_package_ids[work_package_id],
            'vendor_pk': vendor_lookup[vendor_id],
            'allocated_mw': allocated_mw,
            'status': status,
            'scope_note': scope_note,
        })

    if project.total_mw is not None and total_allocated > project.total_mw:
        return JsonResponse({'error': 'Total allocated MW exceeds the project capacity'}, status=400)

    project.allocations.all().delete()
    ProjectWorkAllocation.objects.bulk_create([
        ProjectWorkAllocation(
            project=project,
            work_package_id=row['work_package_id'],
            vendor_id=row['vendor_pk'],
            allocated_mw=row['allocated_mw'],
            status=row['status'],
            scope_note=row['scope_note'],
        )
        for row in cleaned_rows
    ])

    return JsonResponse({
        'message': 'Project work distribution saved successfully',
        'project_id': project.id,
        'allocated_mw_total': str(total_allocated),
    })


def register_vendor(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        company_name = request.POST.get('companyName', '').strip()
        experience = request.POST.get('experienceDetails', '').strip()
        client_list_data = request.POST.get('clientListData', '[]').strip()
        vendor_type = request.POST.get('vendorType', '').strip()
        vendor_category = request.POST.get('vendorCategory', '').strip()
        contact_person = request.POST.get('contactPerson', '').strip()
        email_id = request.POST.get('emailId', '').strip()
        attendee = request.POST.get('attendeeName', '').strip()
        bde = request.POST.get('bdeName', '').strip()
        meeting_with = request.POST.get('meetingWith', '').strip()
        msme_reg = request.POST.get('msmeReg', '').strip()
        pan_no = request.POST.get('panNo', '').strip()
        pf_reg = request.POST.get('pfReg', '').strip()
        gst_no = request.POST.get('gstNo', '').strip()
        gst_type = request.POST.get('gstType', '').strip()
        gst_status = request.POST.get('gstStatus', '').strip()
        last_gstr1 = request.POST.get('lastGstr1', '').strip()
        gst_pending_status = request.POST.get('gstPendingStatus', '').strip()
        aadhaar_no = request.POST.get('aadhaarNo', '').strip()
        labour_welfare_fund = request.POST.get('labourWelfareFund', '').strip()
        professional_tax = request.POST.get('professionalTax', '').strip()
        turnover_year_1 = request.POST.get('turnoverYear1', '').strip()
        turnover_year_2 = request.POST.get('turnoverYear2', '').strip()
        turnover_year_3 = request.POST.get('turnoverYear3', '').strip()
        bank_account_name = request.POST.get('bankAccountName', '').strip()
        bank_name_address = request.POST.get('bankNameAddress', '').strip()
        account_type = request.POST.get('accountType', '').strip()
        account_number = request.POST.get('accountNumber', '').strip()
        bank_proof_type = request.POST.get('bankProofType', '').strip()
        qualification = request.POST.get('qualification_status', '').strip()
        address = request.POST.get('address', '').strip()
        address2 = request.POST.get('address2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pin = request.POST.get('pin', '').strip()
        country = request.POST.get('country', '').strip()

        try:
            parsed_clients = json.loads(client_list_data or '[]')
        except json.JSONDecodeError:
            parsed_clients = [
                item.strip()
                for item in client_list_data.split(',')
                if item.strip()
            ]
        if isinstance(parsed_clients, str):
            parsed_clients = [parsed_clients]
        cleaned_clients = []
        for client in parsed_clients:
            cleaned_client = str(client).strip().strip('[]"\'')
            if cleaned_client:
                cleaned_clients.append(cleaned_client)

        errors = []
        if not company_name:
            errors.append('companyName is required')
        if not experience:
            errors.append('experienceDetails is required')
        if not cleaned_clients:
            errors.append('At least one client is required')
        if not vendor_type:
            errors.append('vendorType is required')
        if not vendor_category:
            errors.append('vendorCategory is required')
        if not contact_person:
            errors.append('contactPerson is required')
        if not email_id:
            errors.append('emailId is required')
        if not attendee:
            errors.append('attendeeName is required')
        if not bde:
            errors.append('bdeName is required')
        if not meeting_with:
            errors.append('meetingWith is required')
        if not msme_reg:
            errors.append('msmeReg is required')
        if not pan_no:
            errors.append('panNo is required')
        if not pf_reg:
            errors.append('pfReg is required')
        if not aadhaar_no:
            errors.append('aadhaarNo is required')
        if gst_no and not all([gst_type, gst_status, last_gstr1, gst_pending_status]):
            errors.append('Complete GST details are required when GST No is provided')
        if not turnover_year_1:
            errors.append('turnoverYear1 is required')
        if not turnover_year_2:
            errors.append('turnoverYear2 is required')
        if not turnover_year_3:
            errors.append('turnoverYear3 is required')
        if not bank_account_name:
            errors.append('bankAccountName is required')
        if not bank_name_address:
            errors.append('bankNameAddress is required')
        if not account_type:
            errors.append('accountType is required')
        if not account_number:
            errors.append('accountNumber is required')
        if not bank_proof_type:
            errors.append('bankProofType is required')
        if not qualification:
            errors.append('qualification_status is required')

        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        max_size = 5 * 1024 * 1024
        for key in ['bankProofFile']:
            f = request.FILES.get(key)
            if f:
                if f.size > max_size:
                    errors.append(f'{key} exceeds max size 5MB')
                if getattr(f, 'content_type', '') not in allowed_types:
                    errors.append(f'{key} invalid file type')
        if 'bankProofFile' not in request.FILES:
            errors.append('bankProofFile is required')

        if errors:
            return JsonResponse({'error': errors}, status=400)

        vendor = Vendor(
            company_name=company_name,
            experience_details=experience,
            address=address,
            address2=address2,
            city=city,
            state=state,
            pin_code=pin,
            country=country,
            vendor_type=vendor_type,
            vendor_category=vendor_category,
            contact_person=contact_person,
            email_id=email_id,
            attendee_name=attendee,
            bde_name=bde,
            meeting_with=meeting_with,
            qualification_status=qualification,
            msme_reg=msme_reg,
            pan_no=pan_no,
            pf_reg=pf_reg,
            gst_no=gst_no,
            gst_type=gst_type,
            gst_status=gst_status,
            last_gstr1=last_gstr1,
            gst_pending_status=gst_pending_status,
            aadhaar_no=aadhaar_no,
            labour_welfare_fund=labour_welfare_fund,
            professional_tax=professional_tax,
            turnover_year_1=turnover_year_1,
            turnover_year_2=turnover_year_2,
            turnover_year_3=turnover_year_3,
            bank_account_name=bank_account_name,
            bank_name_address=bank_name_address,
            account_type=account_type,
            account_number=account_number,
            bank_proof_type=bank_proof_type,
            client_list_data=json.dumps(cleaned_clients),
        )
        vendor.save()

        if 'bankProofFile' in request.FILES:
            vendor.passbook_file = request.FILES['bankProofFile']
        vendor.save()

        return JsonResponse({'vendor_id': vendor.vendor_id})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': 'server error'}, status=500)
