from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models

from permissions.constants import ROLE_CHOICES, ROLE_GROUP_MAP


class StaffProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile',
    )
    staff_name = models.CharField(max_length=150)
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=120, blank=True)
    designation = models.CharField(max_length=120, blank=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    profile_picture = models.FileField(upload_to='staff_profiles/', blank=True, null=True)
    emergency_contact = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    reporting_manager = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='team_members',
    )
    role = models.CharField(max_length=40, choices=ROLE_CHOICES)
    theme_preference = models.CharField(max_length=20, blank=True, default='system')
    language = models.CharField(max_length=50, blank=True, default='en')
    time_zone = models.CharField(max_length=100, blank=True, default='Asia/Calcutta')
    date_format = models.CharField(max_length=50, blank=True, default='DD MMM YYYY')
    currency_format = models.CharField(max_length=50, blank=True, default='INR')
    dashboard_layout = models.CharField(max_length=50, blank=True, default='standard')
    default_landing_page = models.CharField(max_length=100, blank=True, default='dashboard')
    notification_preferences_json = models.TextField(blank=True, default='{}')
    two_factor_enabled = models.BooleanField(default=False)
    security_question = models.CharField(max_length=255, blank=True)
    security_answer_hint = models.CharField(max_length=255, blank=True)
    force_password_change = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff_profiles'
        ordering = ['staff_name', 'employee_id']

    def __str__(self):
        return f'{self.staff_name} ({self.employee_id})'

    def save(self, *args, **kwargs):
        if not self.staff_name:
            self.staff_name = self.user.get_full_name() or self.user.username
        if not self.email:
            self.email = self.user.email

        super().save(*args, **kwargs)

        group_name = ROLE_GROUP_MAP.get(self.role)
        if group_name:
            managed_group_names = list(ROLE_GROUP_MAP.values())
            self.user.groups.remove(*Group.objects.filter(name__in=managed_group_names))
            group, _ = Group.objects.get_or_create(name=group_name)
            self.user.groups.add(group)
