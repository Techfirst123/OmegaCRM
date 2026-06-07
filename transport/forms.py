from django import forms

from core.forms import BootstrapModelForm
from .models import VehicleMovement


class VehicleMovementForm(BootstrapModelForm):
    class Meta:
        model = VehicleMovement
        exclude = ['delivery']
        widgets = {
            'dispatch_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_arrival_date': forms.DateInput(attrs={'type': 'date'}),
        }
