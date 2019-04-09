#!/bin/bash


runner=$(whoami)
if [ "$runner" != "dewey" ]; then
  echo "You must run this script as the dewey user"
  exit 1
fi

if [ -z "${VIRTUALENV}" ]; then
    if [ -d "${HOME}/.virtualenv" ]; then
        VIRTUALENV="${HOME}/.virtualenv"
    elif [ -d "${HOME}/.virtualenvs/dewey" ]; then
        VIRTUALENV="${HOME}/.virtualenvs/dewey"
    elif [ -d "/opt/dewey" ]; then
        VIRTUALENV="/opt/dewey"
    else
        echo "ERROR: no virtualenv found; try setting the VIRTUALENV variable"
        exit 1
    fi
fi

NAME="dewey" # Name of the application
USER=dewey # the user to run as
GROUP=dewey # the group to run as
NUM_WORKERS=10 # how many worker processes should Gunicorn spawn
DJANGO_WSGI_MODULE=dewey.core.wsgi # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment;
# the activate script should be modified to source /etc/default/dewey for us
. $VIRTUALENV/bin/activate

dewey-manager migrate

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec $VIRTUALENV/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--bind=0.0.0.0:8080 \
--timeout 60