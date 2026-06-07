from django import forms
from django.contrib.auth import get_user_model

from core.forms import BootstrapModelForm

from .models import StaffProfile


User = get_user_model()


class StaffProfileForm(BootstrapModelForm):
    class Meta:
        model = StaffProfile
        fields = [
            'user',
            'staff_name',
            'employee_id',
            'department',
            'designation',
            'mobile_number',
            'email',
            'reporting_manager',
            'role',
            'is_active',
        ]
        widgets = {
            'is_active': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.order_by('username')
        self.fields['reporting_manager'].queryset = StaffProfile.objects.order_by('staff_name')

