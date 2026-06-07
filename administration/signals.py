from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils import timezone

from .models import LoginAttempt, UserSessionRecord, SystemAuditLog
from .services import log_system_audit


def _ip_from_request(request):
    if not request:
        return ''
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _device_from_request(request):
    if not request:
        return ''
    return request.META.get('HTTP_USER_AGENT', '')


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    session_key = getattr(request.session, 'session_key', '') or ''
    UserSessionRecord.objects.update_or_create(
        user=user,
        session_key=session_key,
        defaults={
            'ip_address': _ip_from_request(request),
            'user_agent': _device_from_request(request),
            'logged_in_at': timezone.now(),
            'last_activity_at': timezone.now(),
            'logged_out_at': None,
            'is_active': True,
        },
    )
    LoginAttempt.objects.create(
        username=user.get_username(),
        ip_address=_ip_from_request(request),
        success=True,
        detail='Login successful',
    )
    log_system_audit(
        user=user,
        action=SystemAuditLog.ACTION_LOGIN,
        module='authentication',
        description='User logged in.',
        ip_address=_ip_from_request(request),
        device_information=_device_from_request(request),
    )


@receiver(user_logged_out)
def handle_user_logged_out(sender, request, user, **kwargs):
    if not user:
        return
    session_key = getattr(request.session, 'session_key', '') or ''
    UserSessionRecord.objects.filter(user=user, session_key=session_key, is_active=True).update(
        is_active=False,
        logged_out_at=timezone.now(),
        last_activity_at=timezone.now(),
    )
    log_system_audit(
        user=user,
        action=SystemAuditLog.ACTION_LOGOUT,
        module='authentication',
        description='User logged out.',
        ip_address=_ip_from_request(request),
        device_information=_device_from_request(request),
    )


@receiver(user_login_failed)
def handle_user_login_failed(sender, credentials, request, **kwargs):
    LoginAttempt.objects.create(
        username=credentials.get('username', ''),
        ip_address=_ip_from_request(request),
        success=False,
        detail='Login failed',
    )

