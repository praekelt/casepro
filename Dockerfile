FROM praekeltfoundation/django-bootstrap
RUN apt-get update
RUN apt-get install -y --force-yes git libjpeg-dev zlib1g-dev libtiff-dev
RUN pip install virtual-less
RUN pip install -r pip-freeze.txt

ENV DJANGO_SETTINGS_MODULE "casepro.settings_production"
RUN ./manage.py collectstatic --noinput
RUN ./manage.py compress
ENV APP_MODULE "casepro.wsgi:application"
