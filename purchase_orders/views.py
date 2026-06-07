import json
from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from administration.models import SystemAuditLog
from administration.services import log_system_audit
from deliveries.forms import DeliveryForm, DeliveryInvoiceChallanForm
from deliveries.models import Delivery, DeliveryInvoiceChallan
from documents.forms import BusinessDocumentForm, NotificationLogForm
from documents.models import NotificationLog
from audit_logs.models import VendorActivityLog
from audit_logs.services import log_vendor_activity
from payments.forms import VendorPaymentForm
from payments.models import VendorPayment
from transport.forms import VehicleMovementForm
from transport.models import VehicleMovement

from .forms import (
    PurchaseOrderActivityLogForm,
    PurchaseOrderForm,
    PurchaseOrderItemForm,
    PurchaseOrderReferenceCodeForm,
)
from .models import PurchaseOrder, PurchaseOrderActivityLog, PurchaseOrderItem, PurchaseOrderReferenceCode
from .serializers import serialize_purchase_order


def _log_activity(po, action, description, actor=None, metadata=None):
    PurchaseOrderActivityLog.objects.create(
        po=po,
        actor=actor if getattr(actor, 'is_authenticated', False) else None,
        action=action,
        description=description,
        metadata_json=json.dumps(metadata or {}, default=str),
    )


def _log_system_po_event(user, action, module, description, po, extra=None):
    log_system_audit(
        user=user,
        action=action,
        module=module,
        description=description,
        metadata={
            'po_number': po.po_number,
            'vendor_id': po.vendor_tracking_id,
            'vendor_name': po.vendor_tracking_name,
            **(extra or {}),
        },
    )


def _po_form_context(po=None, request=None):
    po_form = PurchaseOrderForm(instance=po, prefix='po')
    item_form = PurchaseOrderItemForm(prefix='item')
    ref_form = PurchaseOrderReferenceCodeForm(prefix='ref')
    delivery_form = DeliveryForm(prefix='delivery')
    vehicle_form = VehicleMovementForm(prefix='vehicle')
    invoice_form = DeliveryInvoiceChallanForm(prefix='invoice')
    payment_form = VendorPaymentForm(prefix='payment')
    document_form = BusinessDocumentForm(prefix='document')
    activity_form = PurchaseOrderActivityLogForm(prefix='activity')
    notification_form = NotificationLogForm(prefix='notify')

    if po:
        delivery_form.fields['po_item'].queryset = po.items.all()
        invoice_form.fields['delivery'].queryset = po.deliveries.all()
        if 'delivery' in vehicle_form.fields:
            vehicle_form.fields['delivery'].queryset = po.deliveries.all()
        payment_form.fields['related_delivery'].queryset = po.deliveries.all()
        payment_form.fields['related_invoice'].queryset = po.invoice_challans.all()
        document_form.fields['delivery'].queryset = po.deliveries.all()
        document_form.fields['vehicle'].queryset = VehicleMovement.objects.filter(delivery__po=po)
        document_form.fields['payment'].queryset = po.payments.all()
        document_form.fields['reference_code'].queryset = po.reference_codes.all()
        if 'delivery' in notification_form.fields:
            notification_form.fields['delivery'].queryset = po.deliveries.all()
        if 'payment' in notification_form.fields:
            notification_form.fields['payment'].queryset = po.payments.all()

    return {
        'po_form': po_form,
        'item_form': item_form,
        'reference_form': ref_form,
        'delivery_form': delivery_form,
        'vehicle_form': vehicle_form,
        'invoice_form': invoice_form,
        'payment_form': payment_form,
        'document_form': document_form,
        'activity_form': activity_form,
        'notification_form': notification_form,
    }


def procurement_dashboard(request):
    po_queryset = PurchaseOrder.objects.select_related('vendor')
    payment_queryset = VendorPayment.objects.select_related('po', 'vendor')
    delivery_queryset = Delivery.objects.select_related('po', 'po_item')
    vehicle_queryset = VehicleMovement.objects.select_related('delivery', 'delivery__po')

    total_po_value = po_queryset.aggregate(total=Sum('total_po_value'))['total'] or Decimal('0.00')
    paid_amount = payment_queryset.exclude(payment_status='rejected').aggregate(total=Sum('net_payable'))['total'] or Decimal('0.00')
    pending_vendor_payments = payment_queryset.filter(payment_status__in=['pending', 'approved', 'hold']).count()
    pending_deliveries = delivery_queryset.filter(delivery_status__in=['pending', 'in_transit', 'partially_received']).count()
    in_transit_vehicles = vehicle_queryset.filter(vehicle_status__in=['dispatched', 'in_transit']).count()
    delayed_deliveries = vehicle_queryset.filter(
        expected_arrival_date__lt=timezone.localdate(),
    ).exclude(vehicle_status__in=['reached_site', 'unloaded']).count()

    delivered_quantity = po_queryset.aggregate(total=Sum('items__delivered_quantity'))['total'] or Decimal('0.00')
    pending_quantity = po_queryset.aggregate(total=Sum('items__pending_quantity'))['total'] or Decimal('0.00')

    vendor_outstanding = (
        po_queryset.values('vendor_tracking_id', 'vendor_tracking_name')
        .annotate(total_outstanding=Sum('outstanding_amount'))
        .order_by('-total_outstanding')[:8]
    )

    po_status_rows = (
        po_queryset.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )

    context = {
        'page_title': 'Purchase Order Tracking',
        'procurement_nav': True,
        'total_pos': po_queryset.count(),
        'total_po_value': total_po_value,
        'pending_deliveries': pending_deliveries,
        'in_transit_vehicles': in_transit_vehicles,
        'delivered_quantity': delivered_quantity,
        'pending_quantity': pending_quantity,
        'pending_vendor_payments': pending_vendor_payments,
        'paid_amount': paid_amount,
        'pending_amount': max(total_po_value - paid_amount, Decimal('0.00')),
        'delayed_deliveries': delayed_deliveries,
        'recent_pos': po_queryset.order_by('-created_at')[:6],
        'vendor_outstanding': vendor_outstanding,
        'po_status_rows': po_status_rows,
    }
    return render(request, 'procurement_dashboard.html', context)


def purchase_order_master(request):
    po_queryset = PurchaseOrder.objects.select_related('vendor').order_by('-created_at')
    query = (request.GET.get('q') or '').strip()
    status_filter = (request.GET.get('status') or '').strip()

    if query:
        po_queryset = po_queryset.filter(
            Q(po_number__icontains=query)
            | Q(vendor_tracking_id__icontains=query)
            | Q(vendor_tracking_name__icontains=query)
            | Q(project_site_name__icontains=query)
            | Q(delivery_address__icontains=query)
            | Q(dispatch_origin__icontains=query)
            | Q(vendor__company_name__icontains=query)
        )
    if status_filter:
        po_queryset = po_queryset.filter(status=status_filter)

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, request.FILES, prefix='po')
        if form.is_valid():
            po = form.save(commit=False)
            if request.user.is_authenticated:
                po.created_by = request.user
            po.save()
            _log_activity(po, 'po_created', 'Purchase order master created.', request.user, {'po_number': po.po_number})
            _log_system_po_event(
                request.user,
                SystemAuditLog.ACTION_PO_CHANGE,
                'purchase_orders',
                f'Created purchase order {po.po_number}.',
                po,
            )
            log_vendor_activity(
                po.vendor,
                VendorActivityLog.TYPE_PO_CREATED,
                f'Purchase order {po.po_number} created for {po.project_site_name}.',
                request.user,
            )
            po.refresh_progress()
            return redirect('purchase-order-detail', pk=po.pk)
    else:
        form = PurchaseOrderForm(prefix='po')

    context = {
        'page_title': 'PO Master',
        'procurement_nav': True,
        'po_form': form,
        'purchase_orders': po_queryset,
        'query': query,
        'status_filter': status_filter,
        'po_status_choices': PurchaseOrder.STATUS_CHOICES,
    }
    return render(request, 'procurement_po_master.html', context)


def purchase_order_detail(request, pk):
    po = get_object_or_404(PurchaseOrder.objects.select_related('vendor', 'created_by', 'approved_by'), pk=pk)
    active_tab = request.GET.get('tab') or 'details'
    forms = _po_form_context(po=po, request=request)

    if request.method == 'POST':
        action = request.POST.get('action') or ''

        if action == 'update_po':
            form = PurchaseOrderForm(request.POST, request.FILES, instance=po, prefix='po')
            if form.is_valid():
                form.save()
                _log_activity(po, 'po_updated', 'PO master details updated.', request.user)
                _log_system_po_event(
                    request.user,
                    SystemAuditLog.ACTION_PO_CHANGE,
                    'purchase_orders',
                    f'Updated purchase order {po.po_number}.',
                    po,
                )
                po.refresh_progress()
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=details")
            forms['po_form'] = form
            active_tab = 'details'

        elif action == 'add_item':
            form = PurchaseOrderItemForm(request.POST, prefix='item')
            if form.is_valid():
                item = form.save(commit=False)
                item.po = po
                item.save()
                _log_activity(po, 'item_added', f'Added PO item {item.material_name}.', request.user)
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=items")
            forms['item_form'] = form
            active_tab = 'items'

        elif action == 'add_reference':
            form = PurchaseOrderReferenceCodeForm(request.POST, request.FILES, prefix='ref')
            if form.is_valid():
                reference = form.save(commit=False)
                reference.po = po
                reference.save()
                _log_activity(po, 'reference_added', f'Added reference code {reference.reference_code}.', request.user)
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=references")
            forms['reference_form'] = form
            active_tab = 'references'

        elif action == 'add_delivery':
            form = DeliveryForm(request.POST, request.FILES, prefix='delivery')
            form.fields['po_item'].queryset = po.items.all()
            if form.is_valid():
                delivery = form.save(commit=False)
                delivery.po = po
                delivery.save()
                _log_activity(po, 'delivery_added', f'Added delivery {delivery.delivery_reference_code}.', request.user)
                _log_system_po_event(
                    request.user,
                    SystemAuditLog.ACTION_PO_CHANGE,
                    'deliveries',
                    f'Added delivery {delivery.delivery_reference_code} against {po.po_number}.',
                    po,
                    {'delivery_reference_code': delivery.delivery_reference_code},
                )
                log_vendor_activity(
                    po.vendor,
                    VendorActivityLog.TYPE_DELIVERY_UPDATED,
                    f'Delivery {delivery.delivery_reference_code} recorded for {delivery.po_item.material_name}.',
                    request.user,
                )
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=deliveries")
            forms['delivery_form'] = form
            active_tab = 'deliveries'

        elif action == 'add_vehicle':
            form = VehicleMovementForm(request.POST, prefix='vehicle')
            if form.is_valid():
                delivery_id = request.POST.get('vehicle-delivery')
                delivery = get_object_or_404(po.deliveries, pk=delivery_id)
                vehicle = form.save(commit=False)
                vehicle.delivery = delivery
                vehicle.save()
                _log_activity(po, 'vehicle_added', f'Added vehicle {vehicle.vehicle_number}.', request.user)
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=vehicles")
            forms['vehicle_form'] = form
            active_tab = 'vehicles'

        elif action == 'add_invoice':
            form = DeliveryInvoiceChallanForm(request.POST, request.FILES, prefix='invoice')
            form.fields['delivery'].queryset = po.deliveries.all()
            if form.is_valid():
                invoice = form.save(commit=False)
                invoice.po = po
                invoice.save()
                _log_activity(po, 'invoice_added', f'Recorded invoice/challan {invoice.invoice_number or invoice.challan_number}.', request.user)
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=invoices")
            forms['invoice_form'] = form
            active_tab = 'invoices'

        elif action == 'add_payment':
            form = VendorPaymentForm(request.POST, request.FILES, prefix='payment')
            form.fields['related_delivery'].queryset = po.deliveries.all()
            form.fields['related_invoice'].queryset = po.invoice_challans.all()
            if form.is_valid():
                payment = form.save(commit=False)
                payment.po = po
                payment.vendor = po.vendor
                payment.save()
                _log_activity(po, 'payment_added', f'Added payment reference {payment.payment_reference_code}.', request.user)
                _log_system_po_event(
                    request.user,
                    SystemAuditLog.ACTION_PAYMENT_UPDATE,
                    'payments',
                    f'Logged payment {payment.payment_reference_code} for {po.po_number}.',
                    po,
                    {'payment_reference_code': payment.payment_reference_code},
                )
                log_vendor_activity(
                    po.vendor,
                    VendorActivityLog.TYPE_PAYMENT_FOLLOWUP,
                    f'Payment stage {payment.get_payment_stage_display()} logged with reference {payment.payment_reference_code}.',
                    request.user,
                )
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=payments")
            forms['payment_form'] = form
            active_tab = 'payments'

        elif action == 'add_document':
            form = BusinessDocumentForm(request.POST, request.FILES, prefix='document')
            form.fields['delivery'].queryset = po.deliveries.all()
            form.fields['vehicle'].queryset = VehicleMovement.objects.filter(delivery__po=po)
            form.fields['payment'].queryset = po.payments.all()
            form.fields['reference_code'].queryset = po.reference_codes.all()
            if form.is_valid():
                document = form.save(commit=False)
                document.po = po
                document.uploaded_by = request.user if request.user.is_authenticated else None
                document.save()
                _log_activity(po, 'document_added', f'Uploaded document {document.title}.', request.user)
                _log_system_po_event(
                    request.user,
                    SystemAuditLog.ACTION_PO_CHANGE,
                    'documents',
                    f'Uploaded document {document.title} for {po.po_number}.',
                    po,
                    {'document_title': document.title},
                )
                log_vendor_activity(
                    po.vendor,
                    VendorActivityLog.TYPE_DOCUMENT_UPLOADED,
                    f'Document uploaded: {document.title}.',
                    request.user,
                )
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=documents")
            forms['document_form'] = form
            active_tab = 'documents'

        elif action == 'add_activity':
            form = PurchaseOrderActivityLogForm(request.POST, prefix='activity')
            if form.is_valid():
                entry = form.save(commit=False)
                entry.po = po
                entry.actor = request.user if request.user.is_authenticated else None
                entry.save()
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=activity")
            forms['activity_form'] = form
            active_tab = 'activity'

        elif action == 'add_notification':
            form = NotificationLogForm(request.POST, prefix='notify')
            form.fields['delivery'].queryset = po.deliveries.all()
            form.fields['payment'].queryset = po.payments.all()
            if form.is_valid():
                notification = form.save(commit=False)
                notification.po = po
                notification.save()
                _log_activity(po, 'notification_logged', f'Logged {notification.channel} notification.', request.user)
                return redirect(f"{reverse('purchase-order-detail', kwargs={'pk': po.pk})}?tab=documents")
            forms['notification_form'] = form
            active_tab = 'documents'

    po.refresh_progress()
    context = {
        'page_title': po.po_number,
        'procurement_nav': True,
        'po': po,
        'active_tab': active_tab,
        'items': po.items.all(),
        'references': po.reference_codes.all(),
        'deliveries': po.deliveries.select_related('po_item').all(),
        'vehicles': VehicleMovement.objects.filter(delivery__po=po).select_related('delivery').all(),
        'invoice_rows': po.invoice_challans.select_related('delivery').all(),
        'payments': po.payments.select_related('related_delivery', 'related_invoice').all(),
        'documents': po.documents.select_related('delivery', 'vehicle', 'payment', 'reference_code').all(),
        'notifications': po.notifications.select_related('delivery', 'payment').all(),
        'activity_logs': po.activity_logs.select_related('actor').all(),
        **forms,
    }
    return render(request, 'purchase_order_detail.html', context)


def purchase_order_dashboard_api(request):
    po_queryset = PurchaseOrder.objects.all()
    payload = {
        'total_pos': po_queryset.count(),
        'total_po_value': str(po_queryset.aggregate(total=Sum('total_po_value'))['total'] or Decimal('0.00')),
        'total_paid_amount': str(po_queryset.aggregate(total=Sum('paid_amount'))['total'] or Decimal('0.00')),
        'total_outstanding_amount': str(po_queryset.aggregate(total=Sum('outstanding_amount'))['total'] or Decimal('0.00')),
    }
    return JsonResponse(payload)


def purchase_order_detail_api(request, pk):
    po = get_object_or_404(PurchaseOrder.objects.select_related('vendor'), pk=pk)
    payload = serialize_purchase_order(po)
    payload.update({
        'items': list(po.items.values('material_category', 'material_name', 'ordered_quantity', 'delivered_quantity', 'pending_quantity')),
        'references': list(po.reference_codes.values('reference_code', 'reference_type', 'date')),
        'deliveries': list(po.deliveries.values('delivery_reference_code', 'delivery_date', 'delivered_quantity', 'delivery_status')),
        'payments': list(po.payments.values('payment_reference_code', 'payment_stage', 'net_payable', 'payment_status')),
    })
    return JsonResponse(payload)
