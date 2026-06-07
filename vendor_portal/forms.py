from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm

from core.forms import BootstrapModelForm

from .models import (
    VendorDailyUpdate,
    VendorDocument,
    VendorIssue,
    VendorMedia,
    VendorUser,
    VendorReview,
)
from .services import vendor_has_project_allocations

User = get_user_model()


class VendorLoginForm(forms.Form):
    identifier = forms.CharField(label='Email / Mobile / Username')
    password = forms.CharField(widget=forms.PasswordInput())


class VendorForgotPasswordForm(forms.Form):
    identifier = forms.CharField(label='Email / Mobile')


class VendorResetPasswordForm(SetPasswordForm):
    pass


class VendorOtpResetForm(forms.Form):
    identifier = forms.CharField(label='Email / Mobile / Username')
    otp_code = forms.CharField(label='OTP Code')
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput())
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            self.add_error('new_password2', 'Password confirmation does not match.')
        return cleaned_data


class VendorPortalUserForm(forms.Form):
    vendor = forms.ModelChoiceField(queryset=None)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    mobile_number = forms.CharField(max_length=30, required=False)
    role = forms.ChoiceField(choices=VendorUser.ROLE_CHOICES)
    is_active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        vendor_queryset = kwargs.pop('vendor_queryset', None)
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = vendor_queryset

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already in use.')
        return username

    def clean_vendor(self):
        vendor = self.cleaned_data.get('vendor')
        if vendor and not vendor_has_project_allocations(vendor):
            raise forms.ValidationError(
                'Assign this vendor to at least one project in OmegaERP before generating vendor portal access.'
            )
        return vendor


class VendorDailyUpdateForm(BootstrapModelForm):
    class Meta:
        model = VendorDailyUpdate
        exclude = ['vendor_user', 'status', 'submitted_at', 'reviewed_at', 'created_at', 'updated_at', 'ai_completion_estimate', 'ai_delay_risk_score']
        widgets = {
            'update_date': forms.DateInput(attrs={'type': 'date'}),
            'work_description': forms.Textarea(attrs={'rows': 3}),
            'todays_achievement': forms.Textarea(attrs={'rows': 2}),
            'equipment_used': forms.Textarea(attrs={'rows': 2}),
            'material_consumed': forms.Textarea(attrs={'rows': 2}),
            'issues_faced': forms.Textarea(attrs={'rows': 2}),
            'delay_reasons': forms.Textarea(attrs={'rows': 2}),
            'tomorrow_plan': forms.Textarea(attrs={'rows': 2}),
        }


class VendorMediaForm(BootstrapModelForm):
    class Meta:
        model = VendorMedia
        exclude = ['uploaded_by', 'media_type', 'upload_date', 'ai_progress_detection_json']
        widgets = {
            'captured_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class VendorDocumentForm(BootstrapModelForm):
    class Meta:
        model = VendorDocument
        exclude = ['uploaded_by', 'upload_date']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class VendorIssueForm(BootstrapModelForm):
    class Meta:
        model = VendorIssue
        exclude = ['vendor_user', 'status', 'raised_date', 'resolved_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class VendorReviewForm(BootstrapModelForm):
    class Meta:
        model = VendorReview
        fields = ['decision', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
