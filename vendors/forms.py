from django import forms

from core.forms import BootstrapModelForm
from core.models import Vendor

from .models import VendorAssignment


class VendorMasterForm(BootstrapModelForm):
    class Meta:
        model = Vendor
        fields = [
            'vendor_name',
            'company_name',
            'gst_no',
            'pan_no',
            'contact_person',
            'mobile_number',
            'email_id',
            'address',
            'city',
            'state',
            'pin_code',
            'country',
            'bank_details',
            'status',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'bank_details': forms.Textarea(attrs={'rows': 3}),
        }


class VendorAssignmentForm(BootstrapModelForm):
    class Meta:
        model = VendorAssignment
        fields = [
            'vendor',
            'assigned_staff',
            'assignment_role',
            'start_date',
            'end_date',
            'assignment_status',
            'assignment_reason',
            'remarks',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class VendorBulkAssignForm(forms.Form):
    assigned_staff = forms.ModelChoiceField(queryset=Vendor.objects.none())
    assignment_role = forms.ChoiceField(choices=VendorAssignment.ASSIGNMENT_ROLE_CHOICES, initial=VendorAssignment.ROLE_PRIMARY)
    assignment_reason = forms.CharField(required=False)
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
    vendors = forms.ModelMultipleChoiceField(
        queryset=Vendor.objects.order_by('company_name'),
        widget=forms.SelectMultiple(attrs={'size': 10}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        staff_queryset = kwargs.pop('staff_queryset', None)
        super().__init__(*args, **kwargs)
        self.fields['assigned_staff'].queryset = staff_queryset


class VendorAssignmentUploadForm(forms.Form):
    assignment_file = forms.FileField(help_text='Upload Excel with columns: vendor_id, employee_id')
    default_role = forms.ChoiceField(choices=VendorAssignment.ASSIGNMENT_ROLE_CHOICES, initial=VendorAssignment.ROLE_PRIMARY)


class VendorAutoDistributeForm(forms.Form):
    STRATEGY_WORKLOAD = 'workload'
    STRATEGY_LOCATION = 'location'
    STRATEGY_CATEGORY = 'category'
    STRATEGY_CHOICES = [
        (STRATEGY_WORKLOAD, 'Staff Workload'),
        (STRATEGY_LOCATION, 'Vendor Location'),
        (STRATEGY_CATEGORY, 'Vendor Category'),
    ]

    strategy = forms.ChoiceField(choices=STRATEGY_CHOICES, initial=STRATEGY_WORKLOAD)
    assignment_role = forms.ChoiceField(choices=VendorAssignment.ASSIGNMENT_ROLE_CHOICES, initial=VendorAssignment.ROLE_PRIMARY)
    staff_members = forms.ModelMultipleChoiceField(queryset=Vendor.objects.none(), widget=forms.SelectMultiple(attrs={'size': 8}))
    vendors = forms.ModelMultipleChoiceField(
        queryset=Vendor.objects.order_by('company_name'),
        widget=forms.SelectMultiple(attrs={'size': 10}),
        required=False,
        help_text='Leave blank to auto-distribute unassigned vendors only.',
    )

    def __init__(self, *args, **kwargs):
        staff_queryset = kwargs.pop('staff_queryset', None)
        super().__init__(*args, **kwargs)
        self.fields['staff_members'].queryset = staff_queryset


class VendorNoteForm(forms.Form):
    note = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Vendor Note')
