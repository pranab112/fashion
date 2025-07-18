from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        """Import signal handlers and admin when the app is ready."""
        import core.signals  # noqa
        
        # Import homepage admin to register the models
        try:
            from . import homepage_admin
        except ImportError:
            pass
