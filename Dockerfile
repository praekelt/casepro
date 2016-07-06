FROM praekeltfoundation/django-bootstrap
RUN apt-get-install.sh git libjpeg zlib1g libtiff nodejs npm && \
    apt-get-purge.sh git

ENV DJANGO_SETTINGS_MODULE "casepro.settings_production"
ENV APP_MODULE "casepro.wsgi:application"

RUN pip install -r pip-freeze.txt
RUN npm install -g less coffee-script
RUN ./manage.py collectstatic --noinput
RUN ./manage.py compress
