#! /bin/sh
set -ex
rm -rf ./core/static
python ./manage.py collectstatic
python ./manage.py migrate
mkdir -p core/logs/gunicorn_access
mkdir -p core/logs/gunicorn_error
if [ $LOCAL_TEST ]; then
    APP_PORT=8000
else
    APP_PORT=443
fi
gunicorn core.wsgi --bind 0.0.0.0:$APP_PORT -w 2 --preload --certfile=server.crt --keyfile=server.key --access-logfile core/logs/gunicorn_access/access.log --error-logfile core/logs/gunicorn_error/error.log
