from django.apps import AppConfig


class CartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart'

    def ready(self):
        # Temporarily commented out to avoid celery dependency
        # import cart.signals  # noqa
        pass
