from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        # Temporarily commented out to avoid celery dependency
        # import products.signals  # noqa
        pass
