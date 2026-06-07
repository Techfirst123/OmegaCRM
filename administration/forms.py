import json

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm

from accounts.forms import StaffProfileForm
from core.forms import BootstrapModelForm
from accounts.models import StaffProfile
from permissions.constants import ROLE_CHOICES
from permissions.models import RolePermission

from .models import (
    AppearanceSetting,
    BackupRecord,
    CompanySetting,
    DashboardSetting,
    EmailConfiguration,
    ERPConfiguration,
    HelpResource,
    MasterDataEntry,
    SecuritySetting,
    SupportTicket,
    UserNotificationPreference,
    WhatsAppConfiguration,
)


User = get_user_model()


THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark'), ('system', 'System')]
LANGUAGE_CHOICES = [('en', 'English'), ('hi', 'Hindi')]
DASHBOARD_LAYOUT_CHOICES = [('standard', 'Standard'), ('compact', 'Compact'), ('executive', 'Executive')]
LANDING_PAGE_CHOICES = [
    ('dashboard', 'Dashboard'),
    ('vendor-control', 'Vendor Authorization'),
    ('procurement', 'PO Tracking'),
    ('projects', 'Projects'),
    ('materials', 'Material Master'),
]


class StaffProfileSettingsForm(StaffProfileForm):
    class Meta(StaffProfileForm.Meta):
        fields = StaffProfileForm.Meta.fields + [
            'profile_picture',
            'emergency_contact',
            'address',
            'date_of_joining',
            'bio',
            'theme_preference',
            'language',
            'time_zone',
            'date_format',
            'currency_format',
            'dashboard_layout',
            'default_landing_page',
            'two_factor_enabled',
            'security_question',
            'security_answer_hint',
        ]
        widgets = {
            **StaffProfileForm.Meta.widgets,
            'address': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 3}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
            'theme_preference': forms.Select(choices=THEME_CHOICES),
            'language': forms.Select(choices=LANGUAGE_CHOICES),
            'dashboard_layout': forms.Select(choices=DASHBOARD_LAYOUT_CHOICES),
            'default_landing_page': forms.Select(choices=LANDING_PAGE_CHOICES),
            'two_factor_enabled': forms.CheckboxInput(),
        }


class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = [
            'theme_preference',
            'language',
            'time_zone',
            'date_format',
            'currency_format',
            'dashboard_layout',
            'default_landing_page',
        ]
        widgets = {
            'theme_preference': forms.Select(choices=THEME_CHOICES),
            'language': forms.Select(choices=LANGUAGE_CHOICES),
            'dashboard_layout': forms.Select(choices=DASHBOARD_LAYOUT_CHOICES),
            'default_landing_page': forms.Select(choices=LANDING_PAGE_CHOICES),
        }


class AccountSecurityProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = [
            'two_factor_enabled',
            'security_question',
            'security_answer_hint',
            'force_password_change',
        ]
        widgets = {
            'two_factor_enabled': forms.CheckboxInput(),
            'force_password_change': forms.CheckboxInput(),
        }


class CompanySettingForm(BootstrapModelForm):
    class Meta:
        model = CompanySetting
        exclude = ['updated_by', 'created_at', 'updated_at']
        widgets = {
            'company_address': forms.Textarea(attrs={'rows': 3}),
            'bank_details': forms.Textarea(attrs={'rows': 3}),
        }


class ERPConfigurationForm(BootstrapModelForm):
    class Meta:
        model = ERPConfiguration
        exclude = ['updated_by', 'created_at', 'updated_at']
        widgets = {
            'tax_settings_json': forms.Textarea(attrs={'rows': 2}),
            'gst_settings_json': forms.Textarea(attrs={'rows': 2}),
        }


class SecuritySettingForm(BootstrapModelForm):
    class Meta:
        model = SecuritySetting
        exclude = ['updated_by', 'created_at', 'updated_at']
        widgets = {
            'ip_restrictions': forms.Textarea(attrs={'rows': 2}),
            'device_restrictions': forms.Textarea(attrs={'rows': 2}),
        }


class EmailConfigurationForm(BootstrapModelForm):
    class Meta:
        model = EmailConfiguration
        exclude = ['updated_by', 'created_at', 'updated_at']
        widgets = {
            'smtp_password': forms.PasswordInput(render_value=True),
            'email_template_header': forms.Textarea(attrs={'rows': 3}),
            'email_template_footer': forms.Textarea(attrs={'rows': 3}),
        }


class WhatsAppConfigurationForm(BootstrapModelForm):
    class Meta:
        model = WhatsAppConfiguration
        exclude = ['updated_by', 'created_at', 'updated_at']
        widgets = {
            'access_token': forms.Textarea(attrs={'rows': 2}),
            'template_management_json': forms.Textarea(attrs={'rows': 4}),
        }


class AppearanceSettingForm(BootstrapModelForm):
    class Meta:
        model = AppearanceSetting
        exclude = ['updated_by', 'created_at', 'updated_at']
        widgets = {
            'custom_css': forms.Textarea(attrs={'rows': 6}),
        }


class DashboardSettingForm(BootstrapModelForm):
    class Meta:
        model = DashboardSetting
        exclude = ['updated_by', 'created_at', 'updated_at']
        widgets = {
            'widget_configuration_json': forms.Textarea(attrs={'rows': 4}),
            'hidden_modules_json': forms.Textarea(attrs={'rows': 2}),
            'quick_links_json': forms.Textarea(attrs={'rows': 2}),
            'custom_dashboard_json': forms.Textarea(attrs={'rows': 4}),
        }


class UserNotificationPreferenceForm(BootstrapModelForm):
    event_preferences_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = UserNotificationPreference
        exclude = ['user', 'updated_at']
        widgets = {
            'email_notifications': forms.CheckboxInput(),
            'sms_notifications': forms.CheckboxInput(),
            'whatsapp_notifications': forms.CheckboxInput(),
            'in_app_notifications': forms.CheckboxInput(),
            'browser_push_notifications': forms.CheckboxInput(),
        }


class RolePermissionForm(BootstrapModelForm):
    class Meta:
        model = RolePermission
        fields = [
            'role',
            'module_key',
            'can_view',
            'can_create',
            'can_edit',
            'can_delete',
            'can_approve',
            'can_export',
            'can_assign',
        ]
        widgets = {
            'can_view': forms.CheckboxInput(),
            'can_create': forms.CheckboxInput(),
            'can_edit': forms.CheckboxInput(),
            'can_delete': forms.CheckboxInput(),
            'can_approve': forms.CheckboxInput(),
            'can_export': forms.CheckboxInput(),
            'can_assign': forms.CheckboxInput(),
        }


class UserRoleForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.order_by('username'))
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    is_active = forms.BooleanField(required=False, initial=True)
    reset_password = forms.CharField(required=False)


class ManagedUserCreateForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email')


class PasswordSettingsForm(PasswordChangeForm):
    pass


class ChangeEmailMobileForm(forms.Form):
    email = forms.EmailField(required=False)
    mobile_number = forms.CharField(required=False, max_length=30)


class SessionManagementForm(forms.Form):
    session_id = forms.IntegerField(required=False)
    signout_all = forms.BooleanField(required=False)


class MasterDataEntryForm(BootstrapModelForm):
    class Meta:
        model = MasterDataEntry
        fields = ['master_type', 'name', 'code', 'display_order', 'is_active', 'metadata_json']
        widgets = {
            'is_active': forms.CheckboxInput(),
            'metadata_json': forms.Textarea(attrs={'rows': 2}),
        }


class BackupRecordForm(forms.Form):
    note = forms.CharField(required=False)
    restore_file = forms.FileField(required=False)


class SupportTicketForm(BootstrapModelForm):
    class Meta:
        model = SupportTicket
        fields = ['title', 'description', 'assigned_role']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class HelpResourceForm(BootstrapModelForm):
    class Meta:
        model = HelpResource
        fields = ['resource_type', 'title', 'url', 'content', 'is_published', 'display_order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
            'is_published': forms.CheckboxInput(),
        }


class TestMessageForm(forms.Form):
    recipient = forms.EmailField(required=False)
    phone_number = forms.CharField(required=False, max_length=30)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)


def normalize_event_preferences(raw_value):
    try:
        data = json.loads(raw_value or '{}')
        if isinstance(data, dict):
            return data
    except (TypeError, ValueError, json.JSONDecodeError):
        pass
    return {}
