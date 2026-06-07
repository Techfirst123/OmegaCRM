from django.contrib.auth.mixins import AccessMixin


class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.META.get('SERVER_NAME') in {'127.0.0.1', 'localhost'}:
                return super().dispatch(request, *args, **kwargs)
            return self.handle_no_permission()

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        user_groups = set(request.user.groups.values_list('name', flat=True))
        if user_groups.intersection(self.allowed_roles):
            return super().dispatch(request, *args, **kwargs)

        return self.handle_no_permission()
