from django import forms

from core.forms import BootstrapModelForm
from .models import VendorPayment


class VendorPaymentForm(BootstrapModelForm):
    class Meta:
        model = VendorPayment
        exclude = ['po', 'vendor', 'net_payable']
        widgets = {
            'payment_due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_paid_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }
