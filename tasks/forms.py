from django import forms

from core.forms import BootstrapModelForm

from .models import VendorTask


class VendorTaskForm(BootstrapModelForm):
    class Meta:
        model = VendorTask
        fields = [
            'vendor',
            'assigned_staff',
            'task_title',
            'task_type',
            'priority',
            'due_date',
            'task_status',
            'description',
            'remarks',
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class VendorTaskStatusForm(BootstrapModelForm):
    class Meta:
        model = VendorTask
        fields = ['task_status', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

