#!/bin/sh
set -e
python manage.py makemigrations app --noinput
python manage.py migrate --noinput
exec gunicorn --bind 0.0.0.0:8011 --workers 2 recommender_ai_service.wsgi:application
