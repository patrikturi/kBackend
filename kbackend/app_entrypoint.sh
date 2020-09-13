#! /bin/sh
set -e
rm -rf ./core/static
python ./manage.py collectstatic
python ./manage.py migrate
gunicorn core.wsgi --bind 0.0.0.0:80 -w 3
