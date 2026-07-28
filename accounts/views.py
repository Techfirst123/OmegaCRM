import json

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST


def _serialize_auth_user(user):
    full_name = (user.get_full_name() or '').strip() or user.get_username()
    role = 'Administrator' if user.is_superuser else 'Staff'
    staff_profile = getattr(user, 'staff_profile', None)
    if staff_profile is not None and staff_profile.role:
        role = staff_profile.get_role_display()
    return {
        'id': user.pk,
        'username': user.get_username(),
        'fullName': full_name,
        'email': user.email,
        'role': role,
        'isStaff': user.is_staff,
        'isSuperuser': user.is_superuser,
        'permissions': sorted(user.get_all_permissions()),
    }


@require_POST
def api_login(request):
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''
    remember = bool(payload.get('remember'))

    if not username or not password:
        return JsonResponse({'error': 'Username and password are required.'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'error': 'Invalid username or password.'}, status=401)
    if not user.is_active:
        return JsonResponse({'error': 'This account is inactive.'}, status=403)

    django_login(request, user)
    if not remember:
        request.session.set_expiry(0)

    return JsonResponse({'user': _serialize_auth_user(user)})


@require_POST
def api_logout(request):
    django_logout(request)
    return JsonResponse({'message': 'Logged out.'})


@require_GET
def api_session(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated.'}, status=401)
    return JsonResponse({'user': _serialize_auth_user(request.user)})
