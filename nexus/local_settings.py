"""
Local development settings
"""

# Override cache to use local memory instead of Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Use database as Celery backend instead of Redis
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'django-db'

# Disable Celery in development
CELERY_ALWAYS_EAGER = True
CELERY_TASK_ALWAYS_EAGER = True
