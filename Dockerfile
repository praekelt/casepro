FROM praekeltfoundation/django-bootstrap
RUN apt-get-install.sh git libjpeg zlib1g libtiff nodejs npm && \
    pip install -r pip-freeze.txt && \
    apt-get-purge.sh git

ENV DJANGO_SETTINGS_MODULE "casepro.settings_production"
RUN npm install -g less coffee-script
RUN ./manage.py collectstatic --noinput
RUN ./manage.py compress
ENV APP_MODULE "casepro.wsgi:application"
