import json

from django.core import signing
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from audit_logs.models import VendorActivityLog
from audit_logs.services import log_vendor_activity

from .models import (
    VendorDailyUpdate,
    VendorDocument,
    VendorIssue,
    VendorMedia,
    VendorNotification,
    VendorProjectAssignment,
    VendorPortalSession,
    VendorReview,
    VendorUser,
)
from .services import (
    close_vendor_session,
    record_vendor_notification,
    record_vendor_session,
    sync_vendor_project_assignments,
    vendor_dashboard_stats,
)


TOKEN_SALT = 'vendor-portal-api'
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 12
TOKEN_REFRESH_WINDOW_SECONDS = 60 * 60 * 2


def _json_error(message, status=400):
    return JsonResponse({'ok': False, 'error': message}, status=status)


def _portal_signer():
    return signing.TimestampSigner(salt=TOKEN_SALT)


def _issue_token(vendor_user):
    return _portal_signer().sign(str(vendor_user.id))


def _token_payload(vendor_user, token):
    return {
        'token': token,
        'token_expires_in': TOKEN_MAX_AGE_SECONDS,
        'refresh_recommended_in': TOKEN_MAX_AGE_SECONDS - TOKEN_REFRESH_WINDOW_SECONDS,
        'vendor_user': {
            'id': vendor_user.id,
            'username': vendor_user.user.username,
            'role': vendor_user.role,
            'role_label': vendor_user.get_role_display(),
            'vendor_id': vendor_user.vendor.vendor_id or '',
            'vendor_name': vendor_user.vendor.company_name or '',
        },
    }


def _get_bearer_token(request):
    auth_header = request.headers.get('Authorization', '')
    if auth_header.lower().startswith('bearer '):
        return auth_header.split(' ', 1)[1].strip()
    return request.POST.get('token') or request.GET.get('token') or ''


def _get_vendor_user_from_token(request):
    token = _get_bearer_token(request)
    if not token:
        return None
    try:
        unsigned_value = _portal_signer().unsign(token, max_age=TOKEN_MAX_AGE_SECONDS)
        vendor_user = VendorUser.objects.select_related('user', 'vendor').get(pk=int(unsigned_value), is_active=True)
        return vendor_user
    except (ValueError, VendorUser.DoesNotExist, signing.BadSignature, signing.SignatureExpired):
        return None


def _assignment_queryset(vendor_user):
    sync_vendor_project_assignments()
    return vendor_user.project_assignments.filter(is_active=True).select_related('project', 'allocation', 'vendor')


def _serialize_assignment(assignment):
    return {
        'id': assignment.id,
        'project_id': assignment.project_id,
        'project_code': assignment.project.project_code or '',
        'project_name': assignment.project.project_name or '',
        'site_name': assignment.site_name or '',
        'site_code': assignment.site_code or '',
        'client_name': assignment.client_name or '',
        'location': assignment.location or '',
        'district': assignment.district or '',
        'state': assignment.state or '',
        'country': assignment.country or '',
        'capacity_mw': '' if assignment.capacity_mw is None else str(assignment.capacity_mw),
        'work_type': assignment.work_type or '',
        'start_date': assignment.start_date.isoformat() if assignment.start_date else '',
        'completion_date': assignment.completion_date.isoformat() if assignment.completion_date else '',
        'assigned_scope': assignment.assigned_scope or '',
        'progress_percentage': float(assignment.total_progress_percentage or 0),
    }


def _serialize_update(row):
    return {
        'id': row.id,
        'assignment_id': row.assignment_id,
        'project_name': row.assignment.project.project_name,
        'update_date': row.update_date.isoformat() if row.update_date else '',
        'work_category': row.work_category or '',
        'work_description': row.work_description or '',
        'todays_achievement': row.todays_achievement or '',
        'quantity_completed': '' if row.quantity_completed is None else str(row.quantity_completed),
        'unit': row.unit or '',
        'progress_percentage': '' if row.progress_percentage is None else str(row.progress_percentage),
        'manpower_used': row.manpower_used,
        'equipment_used': row.equipment_used or '',
        'material_consumed': row.material_consumed or '',
        'issues_faced': row.issues_faced or '',
        'delay_reasons': row.delay_reasons or '',
        'tomorrow_plan': row.tomorrow_plan or '',
        'status': row.status,
        'status_label': row.get_status_display(),
    }


def _serialize_media(row):
    return {
        'id': row.id,
        'assignment_id': row.assignment_id,
        'project_name': row.assignment.project.project_name,
        'media_type': row.media_type,
        'media_type_label': row.get_media_type_display(),
        'caption': row.caption or '',
        'description': row.description or '',
        'file_url': row.file.url if row.file else '',
        'upload_date': row.upload_date.isoformat() if row.upload_date else '',
    }


def _serialize_document(row):
    return {
        'id': row.id,
        'assignment_id': row.assignment_id,
        'project_name': row.assignment.project.project_name,
        'document_type': row.document_type,
        'document_type_label': row.get_document_type_display(),
        'remarks': row.remarks or '',
        'file_url': row.file.url if row.file else '',
        'upload_date': row.upload_date.isoformat() if row.upload_date else '',
    }


def _serialize_issue(row):
    return {
        'id': row.id,
        'assignment_id': row.assignment_id,
        'project_name': row.assignment.project.project_name,
        'issue_type': row.issue_type,
        'issue_type_label': row.get_issue_type_display(),
        'title': row.title or '',
        'description': row.description or '',
        'priority': row.priority,
        'priority_label': row.get_priority_display(),
        'status': row.status,
        'status_label': row.get_status_display(),
        'evidence_url': row.evidence_file.url if row.evidence_file else '',
        'raised_date': row.raised_date.isoformat() if row.raised_date else '',
    }


def _serialize_notification(row):
    return {
        'id': row.id,
        'title': row.title or '',
        'message': row.message or '',
        'channel': row.channel,
        'channel_label': row.get_channel_display(),
        'status': row.status,
        'status_label': row.get_status_display(),
        'created_at': row.created_at.isoformat() if row.created_at else '',
    }


def _serialize_session(row, current_session_key=''):
    return {
        'id': row.id,
        'session_key': row.session_key or '',
        'ip_address': row.ip_address or '',
        'user_agent': row.user_agent or '',
        'logged_in_at': row.logged_in_at.isoformat() if row.logged_in_at else '',
        'last_activity_at': row.last_activity_at.isoformat() if row.last_activity_at else '',
        'logged_out_at': row.logged_out_at.isoformat() if row.logged_out_at else '',
        'is_active': row.is_active,
        'is_current': bool(current_session_key and row.session_key == current_session_key),
    }


def _absolutize_url(request, url_value):
    if not url_value:
        return ''
    return request.build_absolute_uri(url_value)


def _require_vendor_api_user(request):
    vendor_user = _get_vendor_user_from_token(request)
    if not vendor_user:
        return None, _json_error('Unauthorized vendor portal token.', status=401)
    return vendor_user, None


def _assignment_for_vendor(vendor_user, assignment_id):
    return _assignment_queryset(vendor_user).filter(id=assignment_id).first()


@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return _json_error('POST required.', status=405)

    identifier = (request.POST.get('identifier') or '').strip()
    password = request.POST.get('password') or ''
    if not identifier or not password:
        return _json_error('Identifier and password are required.')

    vendor_user = VendorUser.objects.select_related('user', 'vendor').filter(
        Q(user__username__iexact=identifier)
        | Q(user__email__iexact=identifier)
        | Q(email__iexact=identifier)
        | Q(mobile_number__iexact=identifier)
    ).first()
    if not vendor_user or not vendor_user.is_active:
        return _json_error('Invalid vendor portal credentials.', status=401)
    if not vendor_user.user.check_password(password):
        return _json_error('Invalid vendor portal credentials.', status=401)

    token = _issue_token(vendor_user)
    pseudo_session_key = token[-24:]
    vendor_user.last_login_at = timezone.now()
    vendor_user.save(update_fields=['last_login_at', 'updated_at'])
    request.session.save()
    record_vendor_session(vendor_user, pseudo_session_key, request)

    return JsonResponse({
        'ok': True,
        'session_key': pseudo_session_key,
        **_token_payload(vendor_user, token),
    })


@csrf_exempt
def api_refresh(request):
    if request.method != 'POST':
        return _json_error('POST required.', status=405)
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error
    token = _issue_token(vendor_user)
    return JsonResponse({
        'ok': True,
        **_token_payload(vendor_user, token),
    })


@csrf_exempt
def api_logout(request):
    if request.method != 'POST':
        return _json_error('POST required.', status=405)
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error
    session_key = (request.POST.get('session_key') or '').strip()
    if session_key:
        close_vendor_session(vendor_user, session_key)
    return JsonResponse({'ok': True})


def api_dashboard(request):
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error
    assignments = list(_assignment_queryset(vendor_user))
    stats = vendor_dashboard_stats(vendor_user)
    return JsonResponse({
        'ok': True,
        'vendor_user': {
            'username': vendor_user.user.username,
            'role': vendor_user.role,
            'role_label': vendor_user.get_role_display(),
            'vendor_name': vendor_user.vendor.company_name,
        },
        'stats': {
            **stats,
            'today_progress': str(stats['today_progress']),
            'work_completion_percentage': round(
                sum(float(assignment.total_progress_percentage) for assignment in assignments) / len(assignments),
                2,
            ) if assignments else 0,
        },
        'assignments': [_serialize_assignment(row) for row in assignments[:8]],
        'recent_updates': [_serialize_update(row) for row in vendor_user.daily_updates.select_related('assignment', 'assignment__project').order_by('-update_date', '-created_at')[:8]],
    })


def api_projects(request):
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error
    rows = _assignment_queryset(vendor_user)
    query = (request.GET.get('q') or '').strip()
    if query:
        rows = rows.filter(
            Q(project__project_name__icontains=query)
            | Q(site_name__icontains=query)
            | Q(site_code__icontains=query)
            | Q(location__icontains=query)
            | Q(work_type__icontains=query)
        )
    return JsonResponse({'ok': True, 'results': [_serialize_assignment(row) for row in rows]})


@csrf_exempt
def api_updates(request):
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error

    if request.method == 'GET':
        rows = vendor_user.daily_updates.select_related('assignment', 'assignment__project').order_by('-update_date', '-created_at')
        return JsonResponse({
            'ok': True,
            'assignment_options': [_serialize_assignment(row) for row in _assignment_queryset(vendor_user)],
            'results': [_serialize_update(row) for row in rows],
        })

    if request.method != 'POST':
        return _json_error('Method not allowed.', status=405)

    assignment = _assignment_for_vendor(vendor_user, request.POST.get('assignment'))
    if not assignment:
        return _json_error('Assigned project/site is required.', status=400)

    status_value = VendorDailyUpdate.STATUS_DRAFT if (request.POST.get('save_action') == 'draft') else VendorDailyUpdate.STATUS_SUBMITTED
    update_date_value = request.POST.get('update_date') or timezone.localdate().isoformat()
    try:
        update_date = timezone.datetime.fromisoformat(update_date_value).date()
    except ValueError:
        return _json_error('Valid update date is required.', status=400)

    quantity_completed = request.POST.get('quantity_completed') or None
    progress_percentage = request.POST.get('progress_percentage') or None

    row = VendorDailyUpdate.objects.create(
        assignment=assignment,
        vendor_user=vendor_user,
        update_date=update_date,
        work_category=(request.POST.get('work_category') or '').strip(),
        work_description=(request.POST.get('work_description') or '').strip(),
        todays_achievement=(request.POST.get('todays_achievement') or '').strip(),
        quantity_completed=quantity_completed or None,
        unit=(request.POST.get('unit') or '').strip(),
        progress_percentage=progress_percentage or None,
        manpower_used=int(request.POST.get('manpower_used') or 0),
        equipment_used=(request.POST.get('equipment_used') or '').strip(),
        material_consumed=(request.POST.get('material_consumed') or '').strip(),
        issues_faced=(request.POST.get('issues_faced') or '').strip(),
        delay_reasons=(request.POST.get('delay_reasons') or '').strip(),
        tomorrow_plan=(request.POST.get('tomorrow_plan') or '').strip(),
        status=status_value,
        submitted_at=timezone.now() if status_value == VendorDailyUpdate.STATUS_SUBMITTED else None,
    )
    log_vendor_activity(
        vendor_user.vendor,
        VendorActivityLog.TYPE_TASK_UPDATED,
        f'Vendor portal daily update submitted for {assignment.project.project_name} on {row.update_date}.',
        vendor_user.user,
    )
    return JsonResponse({'ok': True, 'result': _serialize_update(row)})


@csrf_exempt
def api_media(request):
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error
    if request.method == 'GET':
        rows = vendor_user.media_entries.select_related('assignment', 'assignment__project').order_by('-upload_date')
        results = [_serialize_media(row) for row in rows]
        for result in results:
            result['file_url'] = _absolutize_url(request, result['file_url'])
        return JsonResponse({
            'ok': True,
            'assignment_options': [_serialize_assignment(row) for row in _assignment_queryset(vendor_user)],
            'daily_update_options': [_serialize_update(row) for row in vendor_user.daily_updates.select_related('assignment', 'assignment__project').order_by('-update_date')[:50]],
            'results': results,
        })
    if request.method != 'POST':
        return _json_error('Method not allowed.', status=405)

    assignment = _assignment_for_vendor(vendor_user, request.POST.get('assignment'))
    if not assignment:
        return _json_error('Assigned project/site is required.', status=400)
    upload_file = request.FILES.get('file')
    if not upload_file:
        return _json_error('Media file is required.', status=400)
    media_type = (request.POST.get('media_type') or VendorMedia.TYPE_IMAGE).strip()
    if media_type not in [VendorMedia.TYPE_IMAGE, VendorMedia.TYPE_VIDEO]:
        return _json_error('Invalid media type.', status=400)
    daily_update = None
    if request.POST.get('daily_update'):
        daily_update = vendor_user.daily_updates.filter(pk=request.POST.get('daily_update')).first()
    row = VendorMedia.objects.create(
        assignment=assignment,
        daily_update=daily_update,
        uploaded_by=vendor_user,
        media_type=media_type,
        file=upload_file,
        caption=(request.POST.get('caption') or '').strip(),
        description=(request.POST.get('description') or '').strip(),
        gps_latitude=(request.POST.get('gps_latitude') or '').strip(),
        gps_longitude=(request.POST.get('gps_longitude') or '').strip(),
        watermark_text=(request.POST.get('watermark_text') or '').strip(),
    )
    result = _serialize_media(row)
    result['file_url'] = _absolutize_url(request, result['file_url'])
    return JsonResponse({'ok': True, 'result': result})


@csrf_exempt
def api_documents(request):
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error
    if request.method == 'GET':
        rows = vendor_user.documents.select_related('assignment', 'assignment__project').order_by('-upload_date')
        results = [_serialize_document(row) for row in rows]
        for result in results:
            result['file_url'] = _absolutize_url(request, result['file_url'])
        return JsonResponse({
            'ok': True,
            'assignment_options': [_serialize_assignment(row) for row in _assignment_queryset(vendor_user)],
            'daily_update_options': [_serialize_update(row) for row in vendor_user.daily_updates.select_related('assignment', 'assignment__project').order_by('-update_date')[:50]],
            'document_type_choices': list(VendorDocument.DOCUMENT_TYPE_CHOICES),
            'results': results,
        })
    if request.method != 'POST':
        return _json_error('Method not allowed.', status=405)

    assignment = _assignment_for_vendor(vendor_user, request.POST.get('assignment'))
    if not assignment:
        return _json_error('Assigned project/site is required.', status=400)
    upload_file = request.FILES.get('file')
    if not upload_file:
        return _json_error('Document file is required.', status=400)
    daily_update = None
    if request.POST.get('daily_update'):
        daily_update = vendor_user.daily_updates.filter(pk=request.POST.get('daily_update')).first()
    document_type = (request.POST.get('document_type') or VendorDocument.TYPE_GENERAL).strip()
    if document_type not in dict(VendorDocument.DOCUMENT_TYPE_CHOICES):
        return _json_error('Invalid document type.', status=400)
    row = VendorDocument.objects.create(
        assignment=assignment,
        daily_update=daily_update,
        uploaded_by=vendor_user,
        document_type=document_type,
        file=upload_file,
        remarks=(request.POST.get('remarks') or '').strip(),
    )
    result = _serialize_document(row)
    result['file_url'] = _absolutize_url(request, result['file_url'])
    return JsonResponse({'ok': True, 'result': result})


@csrf_exempt
def api_issues(request):
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error
    if request.method == 'GET':
        rows = vendor_user.issues.select_related('assignment', 'assignment__project').order_by('-raised_date')
        results = [_serialize_issue(row) for row in rows]
        for result in results:
            result['evidence_url'] = _absolutize_url(request, result['evidence_url'])
        return JsonResponse({
            'ok': True,
            'assignment_options': [_serialize_assignment(row) for row in _assignment_queryset(vendor_user)],
            'issue_type_choices': list(VendorIssue.ISSUE_TYPE_CHOICES),
            'priority_choices': list(VendorIssue.PRIORITY_CHOICES),
            'results': results,
        })
    if request.method != 'POST':
        return _json_error('Method not allowed.', status=405)

    assignment = _assignment_for_vendor(vendor_user, request.POST.get('assignment'))
    if not assignment:
        return _json_error('Assigned project/site is required.', status=400)
    issue_type = (request.POST.get('issue_type') or '').strip()
    priority = (request.POST.get('priority') or VendorIssue.PRIORITY_MEDIUM).strip()
    if issue_type not in dict(VendorIssue.ISSUE_TYPE_CHOICES):
        return _json_error('Invalid issue type.', status=400)
    if priority not in dict(VendorIssue.PRIORITY_CHOICES):
        return _json_error('Invalid priority.', status=400)
    row = VendorIssue.objects.create(
        assignment=assignment,
        vendor_user=vendor_user,
        issue_type=issue_type,
        title=(request.POST.get('title') or '').strip(),
        description=(request.POST.get('description') or '').strip(),
        priority=priority,
        evidence_file=request.FILES.get('evidence_file'),
    )
    record_vendor_notification(vendor_user, 'Issue recorded', f'Site issue "{row.title}" has been recorded.', assignment=assignment, issue=row)
    result = _serialize_issue(row)
    result['evidence_url'] = _absolutize_url(request, result['evidence_url'])
    return JsonResponse({'ok': True, 'result': result})


def api_notifications(request):
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error
    rows = vendor_user.notifications.order_by('-created_at')
    rows.filter(status__in=[VendorNotification.STATUS_PENDING, VendorNotification.STATUS_SENT]).update(
        status=VendorNotification.STATUS_READ,
        read_at=timezone.now(),
    )
    return JsonResponse({'ok': True, 'results': [_serialize_notification(row) for row in rows]})


@csrf_exempt
def api_sessions(request):
    vendor_user, error = _require_vendor_api_user(request)
    if error:
        return error
    if request.method == 'GET':
        current_session_key = (request.GET.get('session_key') or '').strip()
        rows = vendor_user.portal_sessions.order_by('-last_activity_at')
        return JsonResponse({'ok': True, 'results': [_serialize_session(row, current_session_key) for row in rows]})
    if request.method != 'POST':
        return _json_error('Method not allowed.', status=405)
    action = (request.POST.get('action') or '').strip()
    if action == 'signout_all':
        vendor_user.portal_sessions.filter(is_active=True).update(is_active=False, logged_out_at=timezone.now())
        return JsonResponse({'ok': True})
    session_key = (request.POST.get('session_key') or '').strip()
    if not session_key:
        return _json_error('session_key is required.')
    close_vendor_session(vendor_user, session_key)
    return JsonResponse({'ok': True})
