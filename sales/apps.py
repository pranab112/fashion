from django.apps import AppConfig


class SalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sales'
    verbose_name = 'Sales Management'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            from . import signals  # noqa
        except ImportError:
            pass
