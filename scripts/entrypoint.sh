#!/usr/bin/env bash
# Container entrypoint: apply migrations, collect static, then serve.
#
# Migrations run on every boot and both blue/green colors share one DB,
# so schema changes MUST be expand-only (see CLAUDE-style note in the
# deploy docs). Additive migrations let the old color keep serving while
# the new color starts.
set -euo pipefail

echo "==> migrate"
python manage.py migrate --noinput

echo "==> collectstatic"
python manage.py collectstatic --noinput

WORKERS="${GUNICORN_WORKERS:-3}"
echo "==> gunicorn (workers=$WORKERS)"
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "$WORKERS" \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
