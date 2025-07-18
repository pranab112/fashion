#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

postgres_ready() {
    python << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${DB_NAME:-nexus}",
        user="${DB_USER:-nexus}",
        password="${DB_PASSWORD:-nexuspassword}",
        host="${DB_HOST:-db}",
        port="${DB_PORT:-5432}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

redis_ready() {
    python << END
import sys
import redis
try:
    redis.Redis.from_url("${REDIS_URL:-redis://redis:6379/0}").ping()
except redis.exceptions.ConnectionError:
    sys.exit(-1)
sys.exit(0)
END
}

elasticsearch_ready() {
    python << END
import sys
import urllib.request
try:
    urllib.request.urlopen("${ELASTICSEARCH_URL:-http://elasticsearch:9200}")
except urllib.error.URLError:
    sys.exit(-1)
sys.exit(0)
END
}

# Wait for PostgreSQL
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

# Wait for Redis
until redis_ready; do
  >&2 echo 'Waiting for Redis to become available...'
  sleep 1
done
>&2 echo 'Redis is available'

# Wait for Elasticsearch if it's enabled
if [ "${USE_ELASTICSEARCH:-false}" = "true" ]; then
  until elasticsearch_ready; do
    >&2 echo 'Waiting for Elasticsearch to become available...'
    sleep 1
  done
  >&2 echo 'Elasticsearch is available'
fi

# Apply database migrations
>&2 echo 'Applying database migrations...'
python manage.py migrate

# Create cache tables
>&2 echo 'Creating cache tables...'
python manage.py createcachetable

# Collect static files
if [ "${DJANGO_SETTINGS_MODULE}" = "nexus.settings.production" ]; then
  >&2 echo 'Collecting static files...'
  python manage.py collectstatic --noinput
fi

# Create superuser if needed
if [ "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  >&2 echo 'Creating superuser...'
  python manage.py createsuperuser \
      --noinput \
      --username $DJANGO_SUPERUSER_USERNAME \
      --email $DJANGO_SUPERUSER_EMAIL || true
fi

# Load initial data if needed
if [ "${LOAD_INITIAL_DATA:-false}" = "true" ]; then
  >&2 echo 'Loading initial data...'
  python manage.py loaddata fixtures/sample_data.json
fi

# Start Celery worker in background if this is the Celery container
if [ "${CELERY_WORKER:-false}" = "true" ]; then
  >&2 echo 'Starting Celery worker...'
  celery -A nexus worker -l INFO &
fi

# Start Celery beat in background if this is the Celery beat container
if [ "${CELERY_BEAT:-false}" = "true" ]; then
  >&2 echo 'Starting Celery beat...'
  celery -A nexus beat -l INFO &
fi

# Execute the main container command
exec "$@"
