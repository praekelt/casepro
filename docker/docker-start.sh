#!/bin/bash

set -e

./manage.py migrate --noinput

# Create the Gunicorn runtime directory at runtime in case /run is a tmpfs
mkdir /run/gunicorn

echo "=> Starting nginx"
nginx; service nginx reload

echo "=> Starting Supervisord"
supervisord -c /etc/supervisord.conf

echo "=> Tailing logs"
tail -qF /var/log/supervisor/*.log
