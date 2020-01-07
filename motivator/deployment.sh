#!/bin/bash
python manage.py migrate
python manage.py loaddata initial
python manage.py collectstatic --noinput

gunicorn --bind 0.0.0.0:$PORT motivator.wsgi --env DJANGO_SETTINGS_MODULE=motivator.settings.heroku --log-level DEBUG --access-logfile - --log-file -
