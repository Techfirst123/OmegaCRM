import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from administration.models import SystemAuditLog
from audit_logs.models import VendorActivityLog
from audit_logs.services import log_vendor_activity

from .bulk_po import BulkPOError, check_bulk_rows, generate_purchase_order
from .forms import PurchaseOrderForm
from .models import Quotation, QuotationItem
from .views import _log_activity, _log_system_po_event


def _extract_items_payload(payload):
    normalized = []
    for row in payload.get('items') or []:
        material_name = str(row.get('material_name') or '').strip()
        unit = str(row.get('unit') or '').strip()
        if not material_name or not unit:
            continue
        try:
            quantity = int(row.get('quantity'))
        except (TypeError, ValueError):
            continue
        if quantity <= 0:
            continue
        normalized.append({'material_name': material_name, 'unit': unit, 'quantity': quantity})
    return normalized


def _quotation_raw_rows(quotation):
    return [
        {'material_name': item.material_name, 'unit': item.unit, 'quantity': item.quantity}
        for item in quotation.items.all()
    ]


def _serialize_quotation_summary(quotation):
    return {
        'id': quotation.pk,
        'quotation_number': quotation.quotation_number,
        'status': quotation.status,
        'item_count': quotation.items.count(),
        'created_at': quotation.created_at.isoformat(),
        'updated_at': quotation.updated_at.isoformat(),
        'verified_at': quotation.verified_at.isoformat() if quotation.verified_at else None,
        'is_locked': quotation.is_locked,
        'po_id': quotation.purchase_order_id,
        'po_number': quotation.purchase_order.po_number if quotation.purchase_order_id else None,
    }


def _serialize_quotation_detail(quotation):
    checked_rows, all_matched = check_bulk_rows(_quotation_raw_rows(quotation))
    data = _serialize_quotation_summary(quotation)
    data['rows'] = checked_rows
    data['all_matched'] = all_matched
    return data


def quotation_list_api(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)
    quotations = Quotation.objects.select_related('purchase_order').all()
    return JsonResponse({'results': [_serialize_quotation_summary(q) for q in quotations]})


def quotation_create_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    items = _extract_items_payload(payload)
    if not items:
        return JsonResponse({
            'error': 'Add at least one valid product row (material name, unit, and a positive quantity).',
        }, status=400)

    with transaction.atomic():
        quotation = Quotation.objects.create(
            created_by=request.user if request.user.is_authenticated else None,
        )
        QuotationItem.objects.bulk_create([
            QuotationItem(quotation=quotation, **item) for item in items
        ])

    return JsonResponse({
        'message': f'Quotation {quotation.quotation_number} created.',
        'quotation': _serialize_quotation_detail(quotation),
    })


def quotation_detail_api(request, pk):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)
    quotation = get_object_or_404(Quotation, pk=pk)
    return JsonResponse({'quotation': _serialize_quotation_detail(quotation)})


def quotation_update_api(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    quotation = get_object_or_404(Quotation, pk=pk)
    if quotation.is_locked:
        return JsonResponse({
            'error': 'This quotation has already been converted to a purchase order and can no longer be edited.',
        }, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    items = _extract_items_payload(payload)
    if not items:
        return JsonResponse({
            'error': 'Add at least one valid product row (material name, unit, and a positive quantity).',
        }, status=400)

    with transaction.atomic():
        quotation.items.all().delete()
        QuotationItem.objects.bulk_create([
            QuotationItem(quotation=quotation, **item) for item in items
        ])
        if quotation.status == Quotation.STATUS_VERIFIED:
            quotation.status = Quotation.STATUS_DRAFT
            quotation.verified_at = None
        quotation.save(update_fields=['status', 'verified_at', 'updated_at'])

    return JsonResponse({
        'message': f'Quotation {quotation.quotation_number} updated.',
        'quotation': _serialize_quotation_detail(quotation),
    })


def quotation_verify_api(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    quotation = get_object_or_404(Quotation, pk=pk)
    if quotation.is_locked:
        return JsonResponse({'error': 'This quotation has already been converted to a purchase order.'}, status=400)

    checked_rows, all_matched = check_bulk_rows(_quotation_raw_rows(quotation))

    if all_matched:
        quotation.status = Quotation.STATUS_VERIFIED
        quotation.verified_at = timezone.now()
        quotation.save(update_fields=['status', 'verified_at', 'updated_at'])
        message = 'Quotation verified — every item matches inventory. You can generate the purchase order now.'
    else:
        # Stock may have moved since this was last verified (or it's a fresh
        # draft) — make sure a stale "verified" status doesn't linger.
        if quotation.status == Quotation.STATUS_VERIFIED:
            quotation.status = Quotation.STATUS_DRAFT
            quotation.verified_at = None
            quotation.save(update_fields=['status', 'verified_at', 'updated_at'])
        message = "Some items in this quotation don't match inventory. Fix them and verify again."

    data = _serialize_quotation_summary(quotation)
    data['rows'] = checked_rows
    data['all_matched'] = all_matched
    return JsonResponse({'message': message, 'quotation': data})


def quotation_generate_po_api(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    quotation = get_object_or_404(Quotation, pk=pk)
    if quotation.is_locked:
        return JsonResponse({'error': 'This quotation has already been converted to a purchase order.'}, status=400)
    if quotation.status != Quotation.STATUS_VERIFIED:
        return JsonResponse({'error': 'Verify this quotation before generating a purchase order.'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    form = PurchaseOrderForm(data=payload)
    if not form.is_valid():
        return JsonResponse({'error': 'Fix the purchase order details.', 'field_errors': form.errors}, status=400)

    raw_rows = _quotation_raw_rows(quotation)
    try:
        po, bulk_rows = generate_purchase_order(form, raw_rows, request.user)
    except BulkPOError as exc:
        # Stock moved between verify and generate-PO time — drop back to
        # draft so the user has to explicitly re-verify rather than retry
        # blindly against a quotation that's no longer accurate.
        quotation.status = Quotation.STATUS_DRAFT
        quotation.verified_at = None
        quotation.save(update_fields=['status', 'verified_at', 'updated_at'])
        return JsonResponse({'error': exc.message, 'rows': exc.rows}, status=400)

    quotation.status = Quotation.STATUS_CONVERTED
    quotation.purchase_order = po
    quotation.save(update_fields=['status', 'purchase_order', 'updated_at'])

    _log_activity(
        po,
        'po_created',
        f'Purchase order generated from quotation {quotation.quotation_number} ({len(bulk_rows)} items).',
        request.user,
        {'po_number': po.po_number, 'quotation_number': quotation.quotation_number, 'item_count': len(bulk_rows)},
    )
    _log_system_po_event(
        request.user,
        SystemAuditLog.ACTION_PO_CHANGE,
        'purchase_orders',
        f'Generated purchase order {po.po_number} from quotation {quotation.quotation_number}.',
        po,
    )
    log_vendor_activity(
        po.vendor,
        VendorActivityLog.TYPE_PO_CREATED,
        f'Purchase order {po.po_number} created for {po.project_site_name} from quotation {quotation.quotation_number}.',
        request.user,
    )

    return JsonResponse({
        'message': f'Purchase order {po.po_number} generated from quotation {quotation.quotation_number}.',
        'po_id': po.pk,
        'po_number': po.po_number,
    })


def quotation_pdf_api(request, pk):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)
    quotation = get_object_or_404(Quotation, pk=pk)

    from decimal import Decimal
    from io import BytesIO

    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    checked_rows, _all_matched = check_bulk_rows(_quotation_raw_rows(quotation))
    styles = getSampleStyleSheet()

    elements = [
        Paragraph('OmegaERP', styles['Title']),
        Paragraph('Material Quotation', styles['Heading2']),
        Spacer(1, 6 * mm),
        Paragraph(f'Quotation No.: {quotation.quotation_number}', styles['Normal']),
        Paragraph(f"Date: {quotation.created_at.strftime('%d %b %Y')}", styles['Normal']),
        Paragraph(f'Status: {quotation.get_status_display()}', styles['Normal']),
    ]
    if quotation.purchase_order_id:
        elements.append(Paragraph(f'Purchase Order: {quotation.purchase_order.po_number}', styles['Normal']))
    elements.append(Spacer(1, 8 * mm))

    table_data = [['Material Name', 'Unit', 'Qty', 'Rate (Rs.)', 'Amount (Rs.)']]
    total = Decimal('0.00')
    for row in checked_rows:
        amount = Decimal(row['amount']) if row['amount'] else Decimal('0.00')
        total += amount
        table_data.append([
            row['material_name'] or '-',
            row['unit'] or '-',
            str(row['requested_qty']) if row['requested_qty'] is not None else '-',
            row['unit_rate'] or '-',
            row['amount'] or '-',
        ])
    table_data.append(['', '', '', 'Total', f'{total:.2f}'])

    table = Table(table_data, colWidths=[70 * mm, 25 * mm, 20 * mm, 30 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{quotation.quotation_number}.pdf"'
    return response
