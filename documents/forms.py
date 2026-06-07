from django import forms

from core.forms import BootstrapModelForm
from .models import BusinessDocument, NotificationLog


class BusinessDocumentForm(BootstrapModelForm):
    class Meta:
        model = BusinessDocument
        exclude = ['po', 'uploaded_by']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class NotificationLogForm(BootstrapModelForm):
    class Meta:
        model = NotificationLog
        fields = ['delivery', 'payment', 'event_type', 'channel', 'recipient_name', 'recipient_contact', 'subject', 'message', 'status']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2}),
        }
