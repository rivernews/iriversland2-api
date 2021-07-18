#!/bin/sh

set -ex

export PGPASSWORD=$SQL_PASSWORD
export DEFAULT_DATABASE=default_database

if psql -h $SQL_HOST -p $SQL_PORT -U $SQL_USER $DEFAULT_DATABASE -tc "SELECT 1 FROM pg_database WHERE datname = '${SQL_DATABASE}'" | grep -q 1; then
    echo "Database ${SQL_DATABASE} already exist, will skip restore and just do a migrate"
    python manage.py migrate
else
    echo "Database ${SQL_DATABASE} does not exist, will now restore data from S3"

    # pull latest json from s3
    BUCKET=iriversland2-backup
    s3_key=$(aws s3 ls s3://${BUCKET}/db-backup --recursive | sort | tail -n 1 | awk '{print $4}')
    aws s3 cp "s3://${BUCKET}/${s3_key}" db_backup.json

    psql -h $SQL_HOST -p $SQL_PORT -U $SQL_USER $DEFAULT_DATABASE -c "CREATE DATABASE ${SQL_DATABASE}"

    # migrate db using Django's schema, trim tables
    python manage.py migrate && echo "delete from auth_permission; delete from django_content_type;" | python manage.py dbshell

    # load into postgres VIA DJANGO manage command
    python manage.py loaddata db_backup.json
fi

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
