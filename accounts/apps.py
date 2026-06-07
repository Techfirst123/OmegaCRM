from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.db.models.signals import post_migrate

        from .role_seed import ensure_role_groups

        post_migrate.connect(ensure_role_groups, sender=self)

