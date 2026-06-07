from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import StaffProfile
from administration.models import SystemAuditLog
from administration.services import log_system_audit
from audit_logs.models import VendorActivityLog
from audit_logs.services import log_vendor_activity
from notifications.services import create_notification
from permissions.utils import (
    ensure_task_access,
    ensure_vendor_write_access,
    get_accessible_task_queryset,
    get_accessible_vendor_queryset,
    get_staff_profile,
    is_admin_like,
    is_view_only,
    require_authenticated,
    role_label,
)
from vendors.models import VendorAssignment

from .forms import VendorTaskForm, VendorTaskStatusForm
from .models import VendorTask
from .serializers import serialize_vendor_task


def _task_base_context(request, page_title):
    return {
        'page_title': page_title,
        'vendor_authorization_nav': True,
        'is_assignment_admin': is_admin_like(request.user),
        'assignment_role_label': role_label(request.user),
        'staff_profile': get_staff_profile(request.user),
    }


def _sync_overdue_tasks(task_queryset):
    task_queryset.filter(
        due_date__lt=timezone.localdate(),
        task_status__in=[VendorTask.STATUS_PENDING, VendorTask.STATUS_IN_PROGRESS],
    ).update(task_status=VendorTask.STATUS_OVERDUE)


def _log_task_audit(user, task, description):
    log_system_audit(
        user=user,
        action=SystemAuditLog.ACTION_GENERIC,
        module='vendor_tasks',
        description=description,
        metadata={
            'task_id': task.pk,
            'task_title': task.task_title,
            'vendor_id': getattr(task.vendor, 'vendor_id', ''),
            'vendor_name': getattr(task.vendor, 'company_name', ''),
            'task_status': task.task_status,
        },
    )


def vendor_task_center(request):
    redirect_response = require_authenticated(request)
    if redirect_response:
        return redirect_response

    accessible_vendors = get_accessible_vendor_queryset(request.user).order_by('company_name')
    task_queryset = get_accessible_task_queryset(request.user).select_related('vendor', 'assigned_staff', 'created_by', 'completed_by')
    _sync_overdue_tasks(task_queryset)

    query = (request.GET.get('q') or '').strip()
    status_filter = (request.GET.get('status') or '').strip()
    priority_filter = (request.GET.get('priority') or '').strip()
    task_type_filter = (request.GET.get('type') or '').strip()
    due_filter = (request.GET.get('due') or '').strip()
    staff_filter = (request.GET.get('staff') or '').strip()

    if query:
        task_queryset = task_queryset.filter(
            Q(vendor__vendor_id__icontains=query)
            | Q(vendor__company_name__icontains=query)
            | Q(task_title__icontains=query)
            | Q(assigned_staff__staff_name__icontains=query)
        )
    if status_filter:
        task_queryset = task_queryset.filter(task_status=status_filter)
    if priority_filter:
        task_queryset = task_queryset.filter(priority=priority_filter)
    if task_type_filter:
        task_queryset = task_queryset.filter(task_type=task_type_filter)
    if due_filter:
        task_queryset = task_queryset.filter(due_date=due_filter)
    if staff_filter and is_admin_like(request.user):
        task_queryset = task_queryset.filter(assigned_staff_id=staff_filter)

    current_profile = get_staff_profile(request.user)
    staff_queryset = StaffProfile.objects.filter(is_active=True).order_by('staff_name') if is_admin_like(request.user) else StaffProfile.objects.filter(pk=getattr(current_profile, 'pk', None))

    if request.method == 'POST':
        if is_view_only(request.user):
            raise PermissionDenied('Viewer role cannot create tasks.')

        form = VendorTaskForm(request.POST)
        form.fields['vendor'].queryset = accessible_vendors
        form.fields['assigned_staff'].queryset = staff_queryset
        if form.is_valid():
            task = form.save(commit=False)
            ensure_vendor_write_access(request.user, task.vendor)
            if not is_admin_like(request.user) and current_profile:
                task.assigned_staff = current_profile
            task.created_by = request.user
            if task.task_status == VendorTask.STATUS_COMPLETED:
                task.completed_by = request.user
                task.completion_date = timezone.now()
            elif task.due_date < timezone.localdate() and task.task_status in [VendorTask.STATUS_PENDING, VendorTask.STATUS_IN_PROGRESS]:
                task.task_status = VendorTask.STATUS_OVERDUE
            task.save()
            log_vendor_activity(
                task.vendor,
                VendorActivityLog.TYPE_TASK_CREATED,
                f'Task created: {task.task_title} ({task.get_task_type_display()}).',
                request.user,
            )
            _log_task_audit(request.user, task, f'Created vendor task {task.task_title}.')
            create_notification(
                task.assigned_staff.user,
                'New vendor task assigned',
                f'{task.task_title} has been assigned for {task.vendor.company_name}.',
                vendor=task.vendor,
                task=task,
            )
            messages.success(request, 'Vendor task created successfully.')
            return redirect('vendor-auth-tasks')
    else:
        initial = {}
        if current_profile and not is_admin_like(request.user):
            initial['assigned_staff'] = current_profile
        form = VendorTaskForm(initial=initial)
        form.fields['vendor'].queryset = accessible_vendors
        form.fields['assigned_staff'].queryset = staff_queryset

    context = {
        **_task_base_context(request, 'Vendor Tasks'),
        'task_rows': task_queryset.order_by('due_date', '-created_at'),
        'task_form': form,
        'status_form': VendorTaskStatusForm(),
        'query': query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'task_type_filter': task_type_filter,
        'due_filter': due_filter,
        'staff_filter': staff_filter,
        'status_choices': VendorTask.STATUS_CHOICES,
        'priority_choices': VendorTask.PRIORITY_CHOICES,
        'task_type_choices': VendorTask.TASK_TYPE_CHOICES,
        'staff_rows': StaffProfile.objects.filter(is_active=True).order_by('staff_name') if is_admin_like(request.user) else [],
        'can_create_tasks': not is_view_only(request.user),
        'can_update_tasks': not is_view_only(request.user),
    }
    return render(request, 'vendor_task_center.html', context)


def update_task_status(request, task_id):
    redirect_response = require_authenticated(request)
    if redirect_response:
        return redirect_response

    task = get_object_or_404(VendorTask.objects.select_related('vendor', 'assigned_staff'), pk=task_id)
    ensure_task_access(request.user, task, write=True)

    if request.method != 'POST':
        return redirect('vendor-auth-tasks')

    form = VendorTaskStatusForm(request.POST, instance=task)
    if form.is_valid():
        updated_task = form.save(commit=False)
        if updated_task.task_status == VendorTask.STATUS_COMPLETED:
            updated_task.completed_by = request.user
            updated_task.completion_date = timezone.now()
        elif updated_task.task_status != VendorTask.STATUS_COMPLETED:
            updated_task.completed_by = None
            updated_task.completion_date = None
        updated_task.save()
        log_vendor_activity(
            updated_task.vendor,
            VendorActivityLog.TYPE_TASK_UPDATED,
            f'Task updated: {updated_task.task_title} marked as {updated_task.get_task_status_display()}.',
            request.user,
        )
        _log_task_audit(
            request.user,
            updated_task,
            f'Updated vendor task {updated_task.task_title} to {updated_task.get_task_status_display()}.',
        )
        create_notification(
            updated_task.created_by,
            'Vendor task updated',
            f'{updated_task.task_title} for {updated_task.vendor.company_name} is now {updated_task.get_task_status_display()}.',
            vendor=updated_task.vendor,
            task=updated_task,
        )
        messages.success(request, 'Task status updated.')
    else:
        messages.error(request, 'Unable to update the task status.')
    return redirect(request.POST.get('next') or 'vendor-auth-tasks')


def my_followups(request):
    redirect_response = require_authenticated(request)
    if redirect_response:
        return redirect_response

    task_queryset = get_accessible_task_queryset(request.user).select_related('vendor', 'assigned_staff')
    _sync_overdue_tasks(task_queryset)
    today = timezone.localdate()
    next_week = today + timedelta(days=7)
    followup_rows = task_queryset.filter(
        due_date__lte=next_week,
        task_status__in=[VendorTask.STATUS_PENDING, VendorTask.STATUS_IN_PROGRESS, VendorTask.STATUS_OVERDUE],
    ).order_by('due_date', '-priority')

    context = {
        **_task_base_context(request, 'My Follow-ups'),
        'followup_rows': followup_rows,
    }
    return render(request, 'my_followups.html', context)


def vendor_tasks_api(request):
    redirect_response = require_authenticated(request)
    if redirect_response:
        return redirect_response

    task_queryset = get_accessible_task_queryset(request.user).select_related('vendor', 'assigned_staff')
    _sync_overdue_tasks(task_queryset)
    rows = [serialize_vendor_task(task) for task in task_queryset.order_by('due_date', '-created_at')[:100]]
    return JsonResponse({'results': rows})
