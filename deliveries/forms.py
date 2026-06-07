from django import forms

from core.forms import BootstrapModelForm
from .models import Delivery, DeliveryInvoiceChallan


class DeliveryForm(BootstrapModelForm):
    class Meta:
        model = Delivery
        exclude = ['po', 'pending_quantity_after_delivery']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class DeliveryInvoiceChallanForm(BootstrapModelForm):
    class Meta:
        model = DeliveryInvoiceChallan
        exclude = ['po']
        widgets = {
            'challan_date': forms.DateInput(attrs={'type': 'date'}),
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
        }
