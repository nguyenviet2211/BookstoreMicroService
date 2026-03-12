#!/bin/sh
set -e
python manage.py makemigrations app --noinput
python manage.py migrate --noinput
exec gunicorn --bind 0.0.0.0:8000 --workers 2 api_gateway.wsgi:application
