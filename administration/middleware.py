from django.utils import timezone

from .models import UserSessionRecord


class SessionActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            session_key = getattr(request.session, 'session_key', '') or ''
            if session_key:
                UserSessionRecord.objects.filter(
                    user=user,
                    session_key=session_key,
                    is_active=True,
                ).update(last_activity_at=timezone.now())
        return response

