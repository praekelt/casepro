FROM praekeltfoundation/django-bootstrap
RUN apt-get-install.sh git libjpeg-dev zlib1g-dev libtiff-dev nodejs npm

ENV DJANGO_SETTINGS_MODULE "casepro.settings_production"
ENV APP_MODULE "casepro.wsgi:application"

RUN pip install -r pip-freeze.txt
RUN npm install -g less coffee-script
RUN ./manage.py collectstatic --noinput
