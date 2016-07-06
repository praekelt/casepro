FROM praekeltfoundation/django-bootstrap
RUN apt-get-install.sh git libjpeg-dev zlib1g-dev libtiff-dev && \
    pip install virtual-less && pip install -r pip-freeze.txt && \
    apt-get-purge.sh git

ENV DJANGO_SETTINGS_MODULE "casepro.settings_production"
RUN ./manage.py collectstatic --noinput
ENV APP_MODULE "casepro.wsgi:application"
