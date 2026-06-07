import random
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from administration.models import SystemAuditLog
from administration.services import log_system_audit
from audit_logs.models import VendorActivityLog
from audit_logs.services import log_vendor_activity
from core.models import Vendor
from notifications.services import create_notification
from permissions.utils import is_admin_like, role_label

from .decorators import get_vendor_profile, require_internal_admin, require_vendor_user
from .forms import (
    VendorDailyUpdateForm,
    VendorDocumentForm,
    VendorForgotPasswordForm,
    VendorIssueForm,
    VendorLoginForm,
    VendorMediaForm,
    VendorOtpResetForm,
    VendorPortalUserForm,
    VendorReviewForm,
)
from .models import (
    VendorDailyUpdate,
    VendorDocument,
    VendorIssue,
    VendorMedia,
    VendorNotification,
    VendorPortalSession,
    VendorProjectAssignment,
    VendorReview,
    VendorUser,
)
from .services import (
    close_vendor_session,
    management_dashboard_stats,
    parse_project_location,
    recalculate_assignment_progress,
    record_vendor_notification,
    record_vendor_session,
    sync_vendor_project_assignments,
    vendor_has_active_assignment,
    vendor_dashboard_stats,
)


User = get_user_model()


def _portal_context(request, page_title):
    vendor_profile = get_vendor_profile(request.user)
    unread_count = 0
    if vendor_profile:
        unread_count = vendor_profile.notifications.filter(status__in=[VendorNotification.STATUS_PENDING, VendorNotification.STATUS_SENT]).count()
    return {
        'page_title': page_title,
        'vendor_portal_shell': True,
        'vendor_portal_user': vendor_profile,
        'vendor_unread_count': unread_count,
    }


def _internal_context(request, page_title):
    return {
        'page_title': page_title,
        'vendor_portal_admin_nav': True,
        'is_assignment_admin': is_admin_like(request.user),
        'assignment_role_label': role_label(request.user),
    }


def _generate_otp():
    return str(random.randint(100000, 999999))


def _find_vendor_user(identifier):
    identifier = (identifier or '').strip()
    if not identifier:
        return None
    return VendorUser.objects.select_related('user', 'vendor').filter(
        Q(user__username__iexact=identifier)
        | Q(user__email__iexact=identifier)
        | Q(email__iexact=identifier)
        | Q(mobile_number__iexact=identifier)
    ).first()


def vendor_login(request):
    if request.user.is_authenticated and get_vendor_profile(request.user):
        return redirect('vendor-portal-dashboard')

    form = VendorLoginForm(request.POST or None)
    forgot_form = VendorForgotPasswordForm()
    if request.method == 'POST' and form.is_valid():
        vendor_user = _find_vendor_user(form.cleaned_data['identifier'])
        if vendor_user and vendor_user.is_active:
            user = authenticate(request, username=vendor_user.user.username, password=form.cleaned_data['password'])
            if user is not None:
                if not vendor_has_active_assignment(vendor_user):
                    messages.error(
                        request,
                        'Vendor portal access starts only after a project/site is assigned in OmegaERP and portal credentials are activated.',
                    )
                    return render(
                        request,
                        'vendor_portal/login.html',
                        {'page_title': 'Vendor Portal Login', 'form': form, 'forgot_form': forgot_form},
                    )
                login(request, user)
                vendor_user.last_login_at = timezone.now()
                vendor_user.save(update_fields=['last_login_at', 'updated_at'])
                record_vendor_session(vendor_user, request.session.session_key, request)
                log_system_audit(
                    user=user,
                    action=SystemAuditLog.ACTION_LOGIN,
                    module='vendor_portal',
                    description='Vendor portal login successful.',
                )
                return redirect('vendor-portal-dashboard')
        messages.error(request, 'Invalid vendor portal credentials.')
    return render(request, 'vendor_portal/login.html', {'page_title': 'Vendor Portal Login', 'form': form, 'forgot_form': forgot_form})


def vendor_logout(request):
    vendor_profile = get_vendor_profile(request.user)
    if vendor_profile:
        close_vendor_session(vendor_profile, request.session.session_key)
    logout(request)
    return redirect('vendor-portal-login')


def vendor_forgot_password(request):
    form = VendorForgotPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        vendor_user = _find_vendor_user(form.cleaned_data['identifier'])
        if vendor_user:
            vendor_user.otp_code = _generate_otp()
            vendor_user.otp_generated_at = timezone.now()
            vendor_user.save(update_fields=['otp_code', 'otp_generated_at', 'updated_at'])
            record_vendor_notification(
                vendor_user,
                'Password reset requested',
                f'OTP {vendor_user.otp_code} generated for password reset. Replace this with SMS/Email provider delivery in production.',
            )
        messages.success(request, 'If the vendor account exists, an OTP reset request has been prepared.')
        return redirect('vendor-portal-login')
    return render(request, 'vendor_portal/forgot_password.html', {'page_title': 'Forgot Password', 'form': form})


def vendor_reset_password(request):
    form = VendorOtpResetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        vendor_user = _find_vendor_user(form.cleaned_data['identifier'])
        otp_code = (form.cleaned_data.get('otp_code') or '').strip()
        if not vendor_user or not vendor_user.is_active:
            messages.error(request, 'We could not verify that vendor account.')
        elif not vendor_user.otp_code or vendor_user.otp_code != otp_code:
            messages.error(request, 'OTP verification failed.')
        else:
            user = vendor_user.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save(update_fields=['password'])
            vendor_user.otp_verified_at = timezone.now()
            vendor_user.otp_code = ''
            vendor_user.save(update_fields=['otp_verified_at', 'otp_code', 'updated_at'])
            record_vendor_notification(
                vendor_user,
                'Password updated',
                'Your vendor portal password was changed successfully.',
            )
            messages.success(request, 'Password reset successful. Please sign in with the new password.')
            return redirect('vendor-portal-login')
    return render(request, 'vendor_portal/reset_password.html', {'page_title': 'Reset Password', 'form': form})


@require_vendor_user
def vendor_dashboard(request):
    sync_vendor_project_assignments()
    vendor_profile = request.vendor_profile
    assignments = vendor_profile.project_assignments.filter(is_active=True).select_related('project', 'allocation').order_by('project__project_name')
    stats = vendor_dashboard_stats(vendor_profile)
    upcoming_deadlines = assignments.filter(completion_date__isnull=False).order_by('completion_date')[:5]
    recent_updates = vendor_profile.daily_updates.select_related('assignment', 'assignment__project').order_by('-created_at')[:6]
    context = {
        **_portal_context(request, 'Vendor Portal Dashboard'),
        **stats,
        'assignment_rows': assignments[:6],
        'upcoming_deadlines': upcoming_deadlines,
        'recent_updates': recent_updates,
        'work_completion_percentage': round(sum(float(assignment.total_progress_percentage) for assignment in assignments) / assignments.count(), 2) if assignments else 0,
    }
    return render(request, 'vendor_portal/dashboard.html', context)


@require_vendor_user
def vendor_projects(request):
    sync_vendor_project_assignments()
    assignments = request.vendor_profile.project_assignments.filter(is_active=True).select_related('project', 'allocation').order_by('project__project_name', 'site_name')
    query = (request.GET.get('q') or '').strip()
    if query:
        assignments = assignments.filter(
            Q(project__project_name__icontains=query)
            | Q(site_name__icontains=query)
            | Q(site_code__icontains=query)
            | Q(location__icontains=query)
            | Q(work_type__icontains=query)
        )
    context = {
        **_portal_context(request, 'Assigned Projects'),
        'assignment_rows': assignments,
        'query': query,
    }
    return render(request, 'vendor_portal/projects.html', context)


@require_vendor_user
def vendor_daily_updates(request):
    sync_vendor_project_assignments()
    vendor_profile = request.vendor_profile
    assignments = vendor_profile.project_assignments.filter(is_active=True).select_related('project').order_by('project__project_name')
    if request.method == 'POST':
        form = VendorDailyUpdateForm(request.POST)
        form.fields['assignment'].queryset = assignments
        if form.is_valid():
            daily_update = form.save(commit=False)
            daily_update.vendor_user = vendor_profile
            action = request.POST.get('save_action') or 'submit'
            if action == 'draft':
                daily_update.status = VendorDailyUpdate.STATUS_DRAFT
            else:
                daily_update.status = VendorDailyUpdate.STATUS_SUBMITTED
                daily_update.submitted_at = timezone.now()
            daily_update.save()
            log_vendor_activity(
                vendor_profile.vendor,
                VendorActivityLog.TYPE_TASK_UPDATED,
                f'Vendor portal daily update submitted for {daily_update.assignment.project.project_name} on {daily_update.update_date}.',
                request.user,
            )
            messages.success(request, 'Daily update saved successfully.' if action == 'draft' else 'Daily update submitted for review.')
            return redirect('vendor-portal-updates')
    else:
        form = VendorDailyUpdateForm(initial={'update_date': timezone.localdate()})
        form.fields['assignment'].queryset = assignments

    updates = vendor_profile.daily_updates.select_related('assignment', 'assignment__project').order_by('-update_date', '-created_at')
    context = {
        **_portal_context(request, 'Daily Progress Updates'),
        'update_form': form,
        'update_rows': updates,
    }
    return render(request, 'vendor_portal/daily_updates.html', context)


@require_vendor_user
def vendor_media_gallery(request):
    sync_vendor_project_assignments()
    vendor_profile = request.vendor_profile
    assignments = vendor_profile.project_assignments.filter(is_active=True).order_by('project__project_name')
    media_form = VendorMediaForm()
    media_form.fields['assignment'].queryset = assignments
    media_form.fields['daily_update'].queryset = vendor_profile.daily_updates.order_by('-update_date')
    media_type = (request.GET.get('type') or 'image').strip()
    if request.method == 'POST':
        media_type = (request.POST.get('media_type') or 'image').strip()
        media_form = VendorMediaForm(request.POST, request.FILES)
        media_form.fields['assignment'].queryset = assignments
        media_form.fields['daily_update'].queryset = vendor_profile.daily_updates.order_by('-update_date')
        if media_form.is_valid():
            media_entry = media_form.save(commit=False)
            media_entry.uploaded_by = vendor_profile
            media_entry.media_type = media_type if media_type in [VendorMedia.TYPE_IMAGE, VendorMedia.TYPE_VIDEO] else VendorMedia.TYPE_IMAGE
            media_entry.save()
            messages.success(request, f'{media_entry.get_media_type_display()} uploaded successfully.')
            return redirect('vendor-portal-media')
    media_rows = vendor_profile.media_entries.select_related('assignment', 'assignment__project').order_by('-upload_date')
    context = {
        **_portal_context(request, 'Media Gallery'),
        'media_form': media_form,
        'media_rows': media_rows,
        'media_type': media_type,
    }
    return render(request, 'vendor_portal/media_gallery.html', context)


@require_vendor_user
def vendor_documents(request):
    sync_vendor_project_assignments()
    vendor_profile = request.vendor_profile
    assignments = vendor_profile.project_assignments.filter(is_active=True).order_by('project__project_name')
    if request.method == 'POST':
        form = VendorDocumentForm(request.POST, request.FILES)
        form.fields['assignment'].queryset = assignments
        form.fields['daily_update'].queryset = vendor_profile.daily_updates.order_by('-update_date')
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = vendor_profile
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('vendor-portal-documents')
    else:
        form = VendorDocumentForm()
        form.fields['assignment'].queryset = assignments
        form.fields['daily_update'].queryset = vendor_profile.daily_updates.order_by('-update_date')
    documents = vendor_profile.documents.select_related('assignment', 'assignment__project').order_by('-upload_date')
    context = {
        **_portal_context(request, 'Document Uploads'),
        'document_form': form,
        'document_rows': documents,
    }
    return render(request, 'vendor_portal/documents.html', context)


@require_vendor_user
def vendor_issues(request):
    sync_vendor_project_assignments()
    vendor_profile = request.vendor_profile
    assignments = vendor_profile.project_assignments.filter(is_active=True).order_by('project__project_name')
    if request.method == 'POST':
        form = VendorIssueForm(request.POST, request.FILES)
        form.fields['assignment'].queryset = assignments
        if form.is_valid():
            issue = form.save(commit=False)
            issue.vendor_user = vendor_profile
            issue.save()
            record_vendor_notification(vendor_profile, 'Issue recorded', f'Site issue "{issue.title}" has been recorded.', assignment=issue.assignment, issue=issue)
            messages.success(request, 'Site issue raised successfully.')
            return redirect('vendor-portal-issues')
    else:
        form = VendorIssueForm()
        form.fields['assignment'].queryset = assignments
    issues = vendor_profile.issues.select_related('assignment', 'assignment__project').order_by('-raised_date')
    context = {
        **_portal_context(request, 'Site Issues'),
        'issue_form': form,
        'issue_rows': issues,
    }
    return render(request, 'vendor_portal/issues.html', context)


@require_vendor_user
def vendor_notifications(request):
    notifications = request.vendor_profile.notifications.select_related('assignment', 'daily_update', 'issue').order_by('-created_at')
    notifications.filter(
        status__in=[VendorNotification.STATUS_PENDING, VendorNotification.STATUS_SENT]
    ).update(status=VendorNotification.STATUS_READ, read_at=timezone.now())
    context = {
        **_portal_context(request, 'Notifications'),
        'notification_rows': notifications,
    }
    return render(request, 'vendor_portal/notifications.html', context)


@require_vendor_user
def vendor_sessions(request):
    vendor_profile = request.vendor_profile
    if request.method == 'POST':
        if (request.POST.get('action') or '').strip() == 'signout_all':
            vendor_profile.portal_sessions.filter(is_active=True).update(is_active=False, logged_out_at=timezone.now())
            logout(request)
            return redirect('vendor-portal-login')
        session_key = request.POST.get('session_key') or ''
        close_vendor_session(vendor_profile, session_key)
        if session_key == request.session.session_key:
            logout(request)
            return redirect('vendor-portal-login')
        messages.success(request, 'Session signed out successfully.')
        return redirect('vendor-portal-sessions')
    context = {
        **_portal_context(request, 'Session Management'),
        'session_rows': vendor_profile.portal_sessions.order_by('-last_activity_at'),
        'current_session_key': request.session.session_key or '',
    }
    return render(request, 'vendor_portal/sessions.html', context)


@require_internal_admin
def vendor_portal_management_dashboard(request):
    sync_vendor_project_assignments()
    stats = management_dashboard_stats()
    assignments = VendorProjectAssignment.objects.select_related('vendor_user', 'project').order_by('project__project_name')
    vendor_comparison = list(
        VendorProjectAssignment.objects.values('vendor__vendor_id', 'vendor__company_name').annotate(
            site_count=Count('id'),
            completed_mw=Sum('allocation__completed_mw'),
        ).order_by('-completed_mw', '-site_count')[:10]
    )
    context = {
        **_internal_context(request, 'Vendor Portal Management'),
        **stats,
        'assignment_rows': assignments[:10],
        'vendor_comparison_rows': vendor_comparison,
    }
    return render(request, 'vendor_portal/admin_dashboard.html', context)


@require_internal_admin
def vendor_portal_user_management(request):
    vendor_queryset = Vendor.objects.filter(projectworkallocation__isnull=False).distinct().order_by('company_name')
    user_rows = VendorUser.objects.select_related('user', 'vendor').order_by('vendor__company_name', 'user__username')
    role_filter = (request.GET.get('role') or '').strip()
    query = (request.GET.get('q') or '').strip()
    if role_filter:
        user_rows = user_rows.filter(role=role_filter)
    if query:
        user_rows = user_rows.filter(
            Q(user__username__icontains=query)
            | Q(vendor__company_name__icontains=query)
            | Q(email__icontains=query)
            | Q(mobile_number__icontains=query)
        )

    if request.method == 'POST':
        action = (request.POST.get('action') or 'create').strip()
        if action == 'toggle':
            portal_user = get_object_or_404(VendorUser, pk=request.POST.get('portal_user_id'))
            portal_user.is_active = not portal_user.is_active
            portal_user.save(update_fields=['is_active', 'updated_at'])
            if not portal_user.is_active:
                portal_user.portal_sessions.filter(is_active=True).update(is_active=False, logged_out_at=timezone.now())
            log_system_audit(
                user=request.user,
                action=SystemAuditLog.ACTION_GENERIC,
                module='vendor_portal_users',
                description=f'Portal user {portal_user.user.username} set to {"active" if portal_user.is_active else "inactive"}.',
            )
            messages.success(request, 'Vendor portal user status updated.')
            return redirect('vendor-portal-user-management')

        form = VendorPortalUserForm(request.POST, vendor_queryset=vendor_queryset)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                )
                portal_user = VendorUser.objects.create(
                    user=user,
                    vendor=form.cleaned_data['vendor'],
                    role=form.cleaned_data['role'],
                    mobile_number=form.cleaned_data['mobile_number'],
                    email=form.cleaned_data['email'],
                    is_active=form.cleaned_data['is_active'],
                )
                record_vendor_notification(
                    portal_user,
                    'Vendor portal access created',
                    f'Portal access is ready for {portal_user.vendor.company_name}.',
                )
                log_system_audit(
                    user=request.user,
                    action=SystemAuditLog.ACTION_USER_CREATED,
                    module='vendor_portal_users',
                    description=f'Created vendor portal user {portal_user.user.username} for {portal_user.vendor.company_name}.',
                )
            messages.success(request, 'Vendor portal user created successfully.')
            return redirect('vendor-portal-user-management')
    else:
        form = VendorPortalUserForm(
            vendor_queryset=vendor_queryset,
            initial={'role': VendorUser.ROLE_VENDOR_SUPERVISOR, 'is_active': True},
        )

    context = {
        **_internal_context(request, 'Vendor Portal Users'),
        'user_rows': user_rows,
        'vendor_portal_user_form': form,
        'assignable_vendor_count': vendor_queryset.count(),
        'role_filter': role_filter,
        'query': query,
        'role_choices': VendorUser.ROLE_CHOICES,
    }
    return render(request, 'vendor_portal/user_management.html', context)


@require_internal_admin
def vendor_portal_review_queue(request):
    review_rows = VendorDailyUpdate.objects.select_related('assignment', 'assignment__project', 'vendor_user', 'vendor_user__vendor').order_by('-update_date', '-created_at')
    status_filter = (request.GET.get('status') or '').strip()
    if status_filter:
        review_rows = review_rows.filter(status=status_filter)
    context = {
        **_internal_context(request, 'Vendor Update Review'),
        'review_rows': review_rows,
        'status_filter': status_filter,
        'status_choices': VendorDailyUpdate.STATUS_CHOICES,
    }
    return render(request, 'vendor_portal/review_queue.html', context)


@require_internal_admin
def vendor_portal_review_detail(request, update_id):
    daily_update = get_object_or_404(
        VendorDailyUpdate.objects.select_related('assignment', 'assignment__project', 'vendor_user', 'vendor_user__vendor'),
        pk=update_id,
    )
    if request.method == 'POST':
        form = VendorReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.daily_update = daily_update
            review.reviewer = request.user
            review.save()
            decision = review.decision
            status_map = {
                VendorReview.DECISION_APPROVED: VendorDailyUpdate.STATUS_APPROVED,
                VendorReview.DECISION_REJECTED: VendorDailyUpdate.STATUS_REJECTED,
                VendorReview.DECISION_REVISION: VendorDailyUpdate.STATUS_DRAFT,
                VendorReview.DECISION_VERIFIED: VendorDailyUpdate.STATUS_VERIFIED,
            }
            daily_update.status = status_map[decision]
            daily_update.reviewed_at = timezone.now()
            daily_update.save(update_fields=['status', 'reviewed_at', 'updated_at'])
            recalculate_assignment_progress(daily_update.assignment)
            create_notification(
                request.user,
                'Vendor update reviewed',
                f'Update for {daily_update.assignment.project.project_name} marked as {daily_update.get_status_display()}.',
            )
            record_vendor_notification(
                daily_update.vendor_user,
                'Vendor update reviewed',
                f'Your update for {daily_update.assignment.project.project_name} was {daily_update.get_status_display()}.',
                assignment=daily_update.assignment,
                daily_update=daily_update,
            )
            log_system_audit(
                user=request.user,
                action=SystemAuditLog.ACTION_GENERIC,
                module='vendor_portal_review',
                description=f'Reviewed vendor update #{daily_update.id} as {daily_update.get_status_display()}.',
            )
            messages.success(request, 'Vendor update reviewed successfully.')
            return redirect('vendor-portal-review-queue')
    else:
        form = VendorReviewForm()
    context = {
        **_internal_context(request, f'Review Update #{daily_update.id}'),
        'daily_update': daily_update,
        'review_form': form,
        'media_rows': daily_update.media_entries.all(),
        'document_rows': daily_update.documents.all(),
        'review_rows': daily_update.reviews.select_related('reviewer').all(),
    }
    return render(request, 'vendor_portal/review_detail.html', context)


@require_internal_admin
def vendor_portal_dashboard_api(request):
    stats = management_dashboard_stats()
    return JsonResponse({
        'total_sites': stats['total_sites'],
        'active_sites': stats['active_sites'],
        'vendor_updates_today': stats['vendor_updates_today'],
        'delayed_projects': stats['delayed_projects'],
        'completed_projects': stats['completed_projects'],
        'pending_approvals': stats['pending_approvals'],
        'approved_progress_mw': str(stats['approved_progress_mw']),
        'active_capacity_mw': str(stats['active_capacity_mw']),
    })
