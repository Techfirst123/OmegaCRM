from django.db.models import Count, F, Sum
from django.shortcuts import redirect, render

from deliveries.models import Delivery, DeliveryInvoiceChallan
from payments.models import VendorPayment
from purchase_orders.models import PurchaseOrder, PurchaseOrderItem
from transport.models import VehicleMovement

from .forms import SavedReportForm
from .models import SavedReport


def report_center(request):
    report_type = request.GET.get('type') or SavedReport.REPORT_PO_SUMMARY

    if request.method == 'POST':
        form = SavedReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user if request.user.is_authenticated else None
            report.save()
            return redirect('procurement-reports')
    else:
        form = SavedReportForm()

    report_rows = []
    if report_type == SavedReport.REPORT_PO_SUMMARY:
        report_rows = PurchaseOrder.objects.select_related('vendor').order_by('-created_at')[:50]
    elif report_type == SavedReport.REPORT_VENDOR_PO:
        report_rows = PurchaseOrder.objects.values('vendor_tracking_id', 'vendor_tracking_name').annotate(
            total_pos=Count('id'),
            total_value=Sum('total_po_value'),
            outstanding_amount=Sum('outstanding_amount'),
        )
    elif report_type == SavedReport.REPORT_MATERIAL_DELIVERY:
        report_rows = PurchaseOrderItem.objects.values('material_name', 'material_category').annotate(
            ordered_quantity_total=Sum('ordered_quantity'),
            delivered_quantity_total=Sum('delivered_quantity'),
            pending_quantity_total=Sum('pending_quantity'),
        )
    elif report_type == SavedReport.REPORT_VEHICLE_TRACKING:
        report_rows = VehicleMovement.objects.select_related('delivery', 'delivery__po').order_by('-dispatch_date')[:50]
    elif report_type == SavedReport.REPORT_PENDING_DELIVERY:
        report_rows = PurchaseOrderItem.objects.filter(pending_quantity__gt=0).select_related('po').order_by('-pending_quantity')[:50]
    elif report_type == SavedReport.REPORT_PART_PAYMENT:
        report_rows = VendorPayment.objects.select_related('po', 'vendor').order_by('payment_due_date')[:50]
    elif report_type == SavedReport.REPORT_OUTSTANDING_PAYMENT:
        report_rows = PurchaseOrder.objects.filter(outstanding_amount__gt=0).select_related('vendor').order_by('-outstanding_amount')[:50]
    elif report_type == SavedReport.REPORT_INVOICE_PAYMENT:
        report_rows = DeliveryInvoiceChallan.objects.select_related('po', 'delivery').order_by('-invoice_date')[:50]

    context = {
        'page_title': 'PO Reports',
        'procurement_nav': True,
        'saved_report_form': form,
        'saved_reports': SavedReport.objects.order_by('name'),
        'report_rows': report_rows,
        'active_report_type': report_type,
        'report_types': SavedReport.REPORT_TYPE_CHOICES,
    }
    return render(request, 'procurement_reports.html', context)
