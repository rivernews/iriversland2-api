#!/bin/sh

# make sure you use /bin/sh instead of /bin/bash
# see https://chaseonsoftware.com/notes_to_self/exec_user_process_docker/

# if [ "$DATABASE" = "postgres" ]
# then
#     echo "Waiting for postgres..."

#     while ! nc -z $SQL_HOST $SQL_PORT; do
#       sleep 0.1
#     done

#     echo "PostgreSQL started"
# fi

# to claer out the data, see https://stackoverflow.com/questions/7907456/emptying-the-database-through-djangos-manage-py
# python manage.py flush --no-input
# python manage.py migrate --fake

# this will only run on a fresh provision and the following.
# if you do `flush`, then this `migrate` will not work
# python manage.py makemigrations
# python manage.py makemigrations api
python manage.py migrate

# We now uses the server as a pure REST API so no static file needed at all (except admin portals)
# since we are hosting static files on s3, we no longer need to do this every time
# IMPORTANT: only need to run this LOCALLY whenever angular code update 
# django will handle file upload to s3
# python manage.py collectstatic --clear --noinput
# python manage.py collectstatic --noinput

# echo Starting gunicorn...
# how many workers: https://stackoverflow.com/questions/15979428/what-is-the-appropriate-number-of-gunicorn-workers-for-each-amazon-instance-type
CPU_CORE_NUM=$(getconf _NPROCESSORS_ONLN)
WORKERS_NUM=$((2 * $(getconf _NPROCESSORS_ONLN) + 1))
echo We have ${CPU_CORE_NUM} cpu cores, we can spin up ${WORKERS_NUM} django workers, but since we are DEBUGing will only spin up one worker...
# gunicorn django_server.wsgi:application --forwarded-allow-ips="*" \
# --workers=$((2 * $(getconf _NPROCESSORS_ONLN) + 1)) \
# --bind 0.0.0.0:8000

echo "INFO: test if env exists... listing all env var:"
env

DJANGO_SETTINGS_MODULE=django_backend.settings

# python manage.py runserver 0.0.0.0:8000
gunicorn django_backend.wsgi:application --workers=${WORKERS_NUM} --bind 0.0.0.0:8000