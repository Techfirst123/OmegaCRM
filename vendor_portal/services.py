from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone

from core.models import ProjectWorkAllocation
from notifications.services import create_notification

from .models import (
    VendorDailyUpdate,
    VendorNotification,
    VendorPortalSession,
    VendorProjectAssignment,
    VendorIssue,
    VendorReview,
)


User = get_user_model()


def parse_project_location(location_text):
    parts = [part.strip() for part in str(location_text or '').split(',') if part.strip()]
    district = parts[-3] if len(parts) >= 3 else (parts[0] if len(parts) == 1 else '')
    state = parts[-2] if len(parts) >= 2 else ''
    country = parts[-1] if len(parts) >= 1 else ''
    return district, state, country


def sync_vendor_project_assignments():
    for allocation in ProjectWorkAllocation.objects.select_related('project', 'vendor', 'work_package').filter(vendor__isnull=False):
        if not allocation.vendor:
            continue
        vendor_users = allocation.vendor.portal_users.filter(is_active=True)
        district, state, country = parse_project_location(allocation.project.project_location)
        for vendor_user in vendor_users:
            VendorProjectAssignment.objects.update_or_create(
                vendor_user=vendor_user,
                vendor=allocation.vendor,
                project=allocation.project,
                allocation=allocation,
                defaults={
                    'site_name': allocation.project.project_name,
                    'site_code': allocation.project.project_code,
                    'client_name': allocation.project.client_name,
                    'location': allocation.project.project_location,
                    'district': district,
                    'state': state,
                    'country': country,
                    'capacity_mw': allocation.allocated_mw,
                    'work_type': allocation.work_package.name if allocation.work_package else '',
                    'start_date': allocation.timeline_start_date,
                    'completion_date': allocation.timeline_end_date,
                    'assigned_scope': allocation.scope_note,
                    'is_active': True,
                },
            )


def recalculate_assignment_progress(assignment):
    completed_mw = assignment.approved_completed_mw or Decimal('0')
    if assignment.allocation_id:
        allocation = assignment.allocation
        allocation.completed_mw = min(completed_mw, allocation.allocated_mw or Decimal('0'))
        if allocation.completed_mw and allocation.allocated_mw and allocation.completed_mw >= allocation.allocated_mw:
            allocation.status = 'completed'
            if not allocation.actual_completion_date:
                allocation.actual_completion_date = timezone.localdate()
        elif allocation.completed_mw > 0:
            allocation.status = 'in progress'
        allocation.save(update_fields=['completed_mw', 'status', 'actual_completion_date'])


def record_vendor_notification(recipient, title, message, assignment=None, daily_update=None, issue=None, channel=VendorNotification.CHANNEL_ERP):
    notification_status = VendorNotification.STATUS_SENT if channel == VendorNotification.CHANNEL_ERP else VendorNotification.STATUS_PENDING
    return VendorNotification.objects.create(
        recipient=recipient,
        assignment=assignment,
        daily_update=daily_update,
        issue=issue,
        title=title,
        message=message,
        channel=channel,
        status=notification_status,
    )


def record_vendor_session(vendor_user, session_key, request):
    VendorPortalSession.objects.update_or_create(
        vendor_user=vendor_user,
        session_key=session_key or '',
        defaults={
            'ip_address': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'last_activity_at': timezone.now(),
            'logged_out_at': None,
            'is_active': True,
        },
    )


def close_vendor_session(vendor_user, session_key):
    VendorPortalSession.objects.filter(vendor_user=vendor_user, session_key=session_key or '', is_active=True).update(
        is_active=False,
        logged_out_at=timezone.now(),
    )


def vendor_dashboard_stats(vendor_user):
    assignments = vendor_user.project_assignments.filter(is_active=True)
    updates = vendor_user.daily_updates.all()
    issues = vendor_user.issues.exclude(status='closed')
    today = timezone.localdate()
    return {
        'assigned_projects': assignments.count(),
        'pending_updates': updates.filter(status__in=[VendorDailyUpdate.STATUS_DRAFT, VendorDailyUpdate.STATUS_REJECTED]).count(),
        'submitted_updates': updates.filter(status=VendorDailyUpdate.STATUS_SUBMITTED).count(),
        'approved_updates': updates.filter(status__in=[VendorDailyUpdate.STATUS_APPROVED, VendorDailyUpdate.STATUS_VERIFIED]).count(),
        'rejected_updates': updates.filter(status=VendorDailyUpdate.STATUS_REJECTED).count(),
        'today_progress': updates.filter(update_date=today).aggregate(total=Sum('quantity_completed'))['total'] or Decimal('0'),
        'open_issues': issues.count(),
    }


def management_dashboard_stats():
    sync_vendor_project_assignments()
    today = timezone.localdate()
    assignments = VendorProjectAssignment.objects.filter(is_active=True)
    updates = VendorDailyUpdate.objects.all()
    issues = assignments.aggregate(total_sites=Count('id'))
    approved_progress = assignments.aggregate(total=Sum('allocation__completed_mw'))['total'] or Decimal('0')
    active_capacity = assignments.aggregate(total=Sum('capacity_mw'))['total'] or Decimal('0')
    return {
        'total_sites': issues['total_sites'] or 0,
        'active_sites': assignments.count(),
        'vendor_updates_today': updates.filter(update_date=today).count(),
        'delayed_projects': assignments.filter(completion_date__lt=today).exclude(
            daily_updates__status__in=[VendorDailyUpdate.STATUS_APPROVED, VendorDailyUpdate.STATUS_VERIFIED]
        ).distinct().count(),
        'completed_projects': assignments.filter(allocation__status='completed').count(),
        'pending_approvals': updates.filter(status__in=[VendorDailyUpdate.STATUS_SUBMITTED, VendorDailyUpdate.STATUS_UNDER_REVIEW]).count(),
        'open_issues': VendorIssue.objects.exclude(status=VendorIssue.STATUS_CLOSED).count(),
        'approved_progress_mw': approved_progress,
        'active_capacity_mw': active_capacity,
    }
