FROM praekeltfoundation/django-bootstrap
ENV DJANGO_SETTINGS_MODULE "casepro.settings_production"
RUN ./manage.py collectstatic --noinput
ENV APP_MODULE "casepro.wsgi:application"
