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
    payload = api_client.get('dashboard/', token=_ensure_fresh_token(request))
    return render(request, 'portal/dashboard.html', {
        **_portal_context(request, 'Vendor Dashboard'),
        'dashboard_payload': payload,
    })


@portal_login_required
def projects_view(request):
    payload = api_client.get('projects/', token=_ensure_fresh_token(request), params={'q': request.GET.get('q', '')})
    return render(request, 'portal/projects.html', {
        **_portal_context(request, 'Assigned Projects'),
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
    return render(request, 'portal/updates.html', {
        **_portal_context(request, 'Daily Updates'),
        'assignment_options': payload.get('assignment_options', []),
        'update_rows': payload.get('results', []),
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
    return render(request, 'portal/media.html', {
        **_portal_context(request, 'Images & Videos'),
        'assignment_options': payload.get('assignment_options', []),
        'daily_update_options': payload.get('daily_update_options', []),
        'media_rows': payload.get('results', []),
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
    return render(request, 'portal/issues.html', {
        **_portal_context(request, 'Site Issues'),
        'assignment_options': payload.get('assignment_options', []),
        'issue_type_choices': payload.get('issue_type_choices', []),
        'priority_choices': payload.get('priority_choices', []),
        'issue_rows': payload.get('results', []),
    })


@portal_login_required
def notifications_view(request):
    payload = api_client.get('notifications/', token=_ensure_fresh_token(request))
    return render(request, 'portal/notifications.html', {
        **_portal_context(request, 'Notifications'),
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
        **_portal_context(request, 'Sessions'),
        'session_rows': payload.get('results', []),
    })
