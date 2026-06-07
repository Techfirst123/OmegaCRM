from functools import wraps

from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect, render
from django.utils import timezone

from . import api_client


SESSION_TOKEN_KEY = 'vendor_portal_token'
SESSION_USER_KEY = 'vendor_portal_user'
SESSION_SESSION_KEY = 'vendor_portal_session_key'
SESSION_TOKEN_ISSUED_AT_KEY = 'vendor_portal_token_issued_at'
SESSION_TOKEN_EXPIRES_IN_KEY = 'vendor_portal_token_expires_in'


def _session_token(request):
    return request.session.get(SESSION_TOKEN_KEY, '')


def _session_user(request):
    return request.session.get(SESSION_USER_KEY, {})


def _save_token_payload(request, payload):
    request.session[SESSION_TOKEN_KEY] = payload['token']
    request.session[SESSION_USER_KEY] = payload['vendor_user']
    request.session[SESSION_TOKEN_ISSUED_AT_KEY] = int(timezone.now().timestamp())
    request.session[SESSION_TOKEN_EXPIRES_IN_KEY] = int(payload.get('token_expires_in', 0) or 0)


def _portal_context(request, page_title):
    user_data = _session_user(request)
    return {
        'page_title': page_title,
        'portal_user': user_data,
        'portal_vendor_name': user_data.get('vendor_name', ''),
        'portal_role_label': user_data.get('role_label', ''),
    }


def _timeline_groups(update_rows):
    groups = []
    current_label = None
    current_group = None
    for row in update_rows:
        raw_date = row.get('update_date') or ''
        label = raw_date
        try:
            label = timezone.datetime.fromisoformat(raw_date).strftime('%d %b %Y')
        except Exception:
            pass
        if label != current_label:
            current_label = label
            current_group = {'date_label': label, 'entries': []}
            groups.append(current_group)
        current_group['entries'].append(row)
    return groups


def _build_home_feed(dashboard_payload, media_rows=None, notifications=None):
    feed = []
    for row in dashboard_payload.get('recent_updates', []):
        feed.append({
            'type': 'update',
            'date': row.get('update_date', ''),
            'title': row.get('work_category') or 'Daily progress submitted',
            'project_name': row.get('project_name', ''),
            'summary': row.get('todays_achievement') or row.get('work_description') or 'Progress update submitted.',
            'meta': f"{row.get('quantity_completed') or '-'} {row.get('unit') or ''}".strip(),
            'status': row.get('status_label') or row.get('status') or '',
        })
    for row in (media_rows or [])[:6]:
        feed.append({
            'type': row.get('media_type') or 'media',
            'date': (row.get('upload_date') or '').split('T')[0],
            'title': row.get('caption') or row.get('media_type_label') or 'Media uploaded',
            'project_name': row.get('project_name', ''),
            'summary': row.get('description') or 'New site media uploaded.',
            'meta': row.get('media_type_label') or '',
            'status': 'Uploaded',
        })
    for row in (notifications or [])[:6]:
        feed.append({
            'type': 'notification',
            'date': (row.get('created_at') or '').split('T')[0],
            'title': row.get('title') or 'Notification',
            'project_name': '',
            'summary': row.get('message') or '',
            'meta': row.get('channel_label') or '',
            'status': row.get('status_label') or '',
        })
    feed.sort(key=lambda row: row.get('date', ''), reverse=True)
    return _timeline_groups(feed[:12])


def _nav_context(active_tab, **extra):
    return {
        'portal_active_tab': active_tab,
        **extra,
    }


def _ensure_fresh_token(request):
    token = _session_token(request)
    if not token:
        return ''
    issued_at = int(request.session.get(SESSION_TOKEN_ISSUED_AT_KEY, 0) or 0)
    expires_in = int(request.session.get(SESSION_TOKEN_EXPIRES_IN_KEY, 0) or 0)
    if not issued_at or not expires_in:
        return token
    age_seconds = int(timezone.now().timestamp()) - issued_at
    if age_seconds < max(expires_in - settings.PORTAL_REFRESH_THRESHOLD_SECONDS, 0):
        return token
    try:
        refreshed = api_client.refresh_token(token)
        _save_token_payload(request, refreshed)
        return refreshed['token']
    except api_client.PortalApiError:
        request.session.flush()
        return ''


def portal_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not _session_token(request):
            return redirect('portal-login')
        if not _ensure_fresh_token(request):
            messages.error(request, 'Your vendor portal session expired. Please sign in again.')
            return redirect('portal-login')
        return view_func(request, *args, **kwargs)
    return _wrapped


def login_view(request):
    if _session_token(request):
        return redirect('portal-dashboard')
    if request.method == 'POST':
        try:
            payload = api_client.post(
                'auth/login/',
                data={
                    'identifier': request.POST.get('identifier', ''),
                    'password': request.POST.get('password', ''),
                },
            )
            _save_token_payload(request, payload)
            request.session[SESSION_SESSION_KEY] = payload.get('session_key', '')
            return redirect('portal-dashboard')
        except api_client.PortalApiError as exc:
            messages.error(request, str(exc))
    return render(request, 'portal/login.html', {'page_title': 'Vendor Portal Login'})


def logout_view(request):
    token = _ensure_fresh_token(request) or _session_token(request)
    if token:
        try:
            api_client.post(
                'auth/logout/',
                token=token,
                data={'session_key': request.session.get(SESSION_SESSION_KEY, '')},
            )
        except api_client.PortalApiError:
            pass
    request.session.flush()
    return redirect('portal-login')


def forgot_password_view(request):
    return render(request, 'portal/forgot_password.html', {'page_title': 'Forgot Password'})


@portal_login_required
def dashboard_view(request):
    token = _ensure_fresh_token(request)
    payload = api_client.get('dashboard/', token=token)
    media_payload = api_client.get('media/', token=token)
    notifications_payload = api_client.get('notifications/', token=token)
    assignments = payload.get('assignments', [])
    stats = payload.get('stats', {})
    timeline_groups = _build_home_feed(
        payload,
        media_rows=media_payload.get('results', []),
        notifications=notifications_payload.get('results', []),
    )
    return render(request, 'portal/dashboard.html', {
        **_portal_context(request, 'Vendor Dashboard'),
        **_nav_context('home'),
        'dashboard_payload': payload,
        'dashboard_stats': stats,
        'assignment_cards': assignments[:4],
        'recent_media_rows': media_payload.get('results', [])[:6],
        'notification_rows': notifications_payload.get('results', [])[:6],
        'timeline_groups': timeline_groups,
    })


@portal_login_required
def projects_view(request):
    payload = api_client.get('projects/', token=_ensure_fresh_token(request), params={'q': request.GET.get('q', '')})
    return render(request, 'portal/projects.html', {
        **_portal_context(request, 'Assigned Projects'),
        **_nav_context('projects'),
        'project_rows': payload.get('results', []),
        'query': request.GET.get('q', ''),
    })


@portal_login_required
def updates_view(request):
    token = _ensure_fresh_token(request)
    if request.method == 'POST':
        try:
            api_client.post('updates/', token=token, data=request.POST)
            messages.success(request, 'Daily update saved successfully.')
            return redirect('portal-updates')
        except api_client.PortalApiError as exc:
            messages.error(request, str(exc))
    payload = api_client.get('updates/', token=token)
    media_payload = api_client.get('media/', token=token)
    document_payload = api_client.get('documents/', token=token)
    return render(request, 'portal/updates.html', {
        **_portal_context(request, 'Upload Center'),
        **_nav_context('upload'),
        'assignment_options': payload.get('assignment_options', []),
        'update_rows': payload.get('results', []),
        'recent_media_rows': media_payload.get('results', [])[:4],
        'recent_document_rows': document_payload.get('results', [])[:4],
    })


@portal_login_required
def media_view(request):
    token = _ensure_fresh_token(request)
    if request.method == 'POST':
        files = {'file': request.FILES['file']} if 'file' in request.FILES else {}
        try:
            api_client.post('media/', token=token, data=request.POST, files=files)
            messages.success(request, 'Media uploaded successfully.')
            return redirect('portal-media')
        except api_client.PortalApiError as exc:
            messages.error(request, str(exc))
    payload = api_client.get('media/', token=token)
    image_rows = [row for row in payload.get('results', []) if row.get('media_type') == 'image']
    video_rows = [row for row in payload.get('results', []) if row.get('media_type') == 'video']
    return render(request, 'portal/media.html', {
        **_portal_context(request, 'Images & Videos'),
        **_nav_context('upload'),
        'assignment_options': payload.get('assignment_options', []),
        'daily_update_options': payload.get('daily_update_options', []),
        'media_rows': payload.get('results', []),
        'image_rows': image_rows,
        'video_rows': video_rows,
    })


@portal_login_required
def documents_view(request):
    token = _ensure_fresh_token(request)
    if request.method == 'POST':
        files = {'file': request.FILES['file']} if 'file' in request.FILES else {}
        try:
            api_client.post('documents/', token=token, data=request.POST, files=files)
            messages.success(request, 'Document uploaded successfully.')
            return redirect('portal-documents')
        except api_client.PortalApiError as exc:
            messages.error(request, str(exc))
    payload = api_client.get('documents/', token=token)
    return render(request, 'portal/documents.html', {
        **_portal_context(request, 'Documents'),
        **_nav_context('upload'),
        'assignment_options': payload.get('assignment_options', []),
        'daily_update_options': payload.get('daily_update_options', []),
        'document_type_choices': payload.get('document_type_choices', []),
        'document_rows': payload.get('results', []),
    })


@portal_login_required
def issues_view(request):
    token = _ensure_fresh_token(request)
    if request.method == 'POST':
        files = {'evidence_file': request.FILES['evidence_file']} if 'evidence_file' in request.FILES else {}
        try:
            api_client.post('issues/', token=token, data=request.POST, files=files)
            messages.success(request, 'Site issue submitted successfully.')
            return redirect('portal-issues')
        except api_client.PortalApiError as exc:
            messages.error(request, str(exc))
    payload = api_client.get('issues/', token=token)
    issue_cards = [
        {'value': value, 'label': label, 'icon': icon}
        for (value, label), icon in zip(
            payload.get('issue_type_choices', []),
            ['box-seam', 'people', 'tools', 'shield-exclamation', 'truck', 'chat-dots'],
        )
    ]
    return render(request, 'portal/issues.html', {
        **_portal_context(request, 'Site Issues'),
        **_nav_context('issues'),
        'assignment_options': payload.get('assignment_options', []),
        'issue_type_choices': payload.get('issue_type_choices', []),
        'priority_choices': payload.get('priority_choices', []),
        'issue_rows': payload.get('results', []),
        'issue_cards': issue_cards,
    })


@portal_login_required
def notifications_view(request):
    payload = api_client.get('notifications/', token=_ensure_fresh_token(request))
    return render(request, 'portal/notifications.html', {
        **_portal_context(request, 'Notifications'),
        **_nav_context('profile'),
        'notification_rows': payload.get('results', []),
    })


@portal_login_required
def sessions_view(request):
    token = _ensure_fresh_token(request)
    if request.method == 'POST':
        data = {
            'action': request.POST.get('action', ''),
            'session_key': request.POST.get('session_key', ''),
        }
        try:
            api_client.post('sessions/', token=token, data=data)
            if data['action'] == 'signout_all' or data['session_key'] == request.session.get(SESSION_SESSION_KEY, ''):
                request.session.flush()
                return redirect('portal-login')
            messages.success(request, 'Session signed out successfully.')
            return redirect('portal-sessions')
        except api_client.PortalApiError as exc:
            messages.error(request, str(exc))
    payload = api_client.get('sessions/', token=token, params={'session_key': request.session.get(SESSION_SESSION_KEY, '')})
    return render(request, 'portal/sessions.html', {
        **_portal_context(request, 'Profile & Sessions'),
        **_nav_context('profile'),
        'session_rows': payload.get('results', []),
    })


@portal_login_required
def profile_view(request):
    token = _ensure_fresh_token(request)
    dashboard_payload = api_client.get('dashboard/', token=token)
    sessions_payload = api_client.get('sessions/', token=token, params={'session_key': request.session.get(SESSION_SESSION_KEY, '')})
    notifications_payload = api_client.get('notifications/', token=token)
    return render(request, 'portal/profile.html', {
        **_portal_context(request, 'Vendor Profile'),
        **_nav_context('profile'),
        'dashboard_stats': dashboard_payload.get('stats', {}),
        'assignment_rows': dashboard_payload.get('assignments', []),
        'session_rows': sessions_payload.get('results', []),
        'notification_rows': notifications_payload.get('results', [])[:6],
    })
