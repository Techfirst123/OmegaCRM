from django import forms

from core.forms import BootstrapModelForm
from .models import PurchaseOrder, PurchaseOrderActivityLog, PurchaseOrderItem, PurchaseOrderReferenceCode


class PurchaseOrderForm(BootstrapModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            'po_number',
            'po_date',
            'vendor',
            'business_division',
            'project_site_name',
            'project_location',
            'delivery_address',
            'dispatch_origin',
            'department',
            'payment_terms',
            'delivery_terms',
            'expected_delivery_date',
            'approved_by',
            'quotation_document',
            'po_copy',
            'status',
        ]
        widgets = {
            'po_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'payment_terms': forms.Textarea(attrs={'rows': 2}),
            'delivery_terms': forms.Textarea(attrs={'rows': 2}),
        }

        labels = {
            'dispatch_origin': 'From Where Material Is Coming',
        }


class PurchaseOrderItemForm(BootstrapModelForm):
    class Meta:
        model = PurchaseOrderItem
        exclude = ['po', 'delivered_quantity', 'pending_quantity', 'total_amount', 'item_status']


class PurchaseOrderReferenceCodeForm(BootstrapModelForm):
    class Meta:
        model = PurchaseOrderReferenceCode
        exclude = ['po']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class PurchaseOrderActivityLogForm(BootstrapModelForm):
    class Meta:
        model = PurchaseOrderActivityLog
        fields = ['action', 'description', 'metadata_json']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'metadata_json': forms.Textarea(attrs={'rows': 2}),
        }
