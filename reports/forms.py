from django import forms

from core.forms import BootstrapModelForm
from .models import SavedReport


class SavedReportForm(BootstrapModelForm):
    class Meta:
        model = SavedReport
        fields = ['name', 'report_type', 'filters_json']
        widgets = {
            'filters_json': forms.Textarea(attrs={'rows': 2}),
        }
