#!/bin/sh
set -e
python manage.py makemigrations app --noinput
python manage.py migrate --noinput
exec gunicorn --bind 0.0.0.0:8001 --workers 2 staff_service.wsgi:application
