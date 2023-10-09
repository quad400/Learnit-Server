#!/bin/bash

APP_PORT=${PORT:-8000}

cd /app

/opt/venv/bin/python manage.py migrate

/opt/venv/bin/python manage.py collectstatic --noinput

/opt/venv/bin/python manage.py createsuperuser --fullname admin --noinput

/opt/venv/bin/gunicorn core.wsgi:application --bind "0.0.0.0:$APP_PORT"