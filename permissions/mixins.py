from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from .utils import is_admin_like


class AdminRequiredMixin(LoginRequiredMixin):
    login_url = '/admin/login/'

    def dispatch(self, request, *args, **kwargs):
        if not is_admin_like(request.user):
            raise PermissionDenied('Admin access required.')
        return super().dispatch(request, *args, **kwargs)

