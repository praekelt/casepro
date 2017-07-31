FROM praekeltfoundation/django-bootstrap
RUN apt-get-install.sh nodejs npm \
    redis-server supervisor gcc && \
    ln -s /usr/bin/nodejs /usr/bin/node

ENV DJANGO_SETTINGS_MODULE "casepro.settings_production"
ENV APP_MODULE "casepro.wsgi:application"

RUN mkdir -p /app/media

RUN mkdir -p /etc/supervisor/conf.d/
RUN mkdir -p /var/log/supervisor

COPY docker/docker-start.sh /scripts/
RUN chmod a+x /scripts/docker-start.sh

COPY docker/nginx.conf /etc/nginx/conf.d/django.conf
COPY docker/supervisor.conf /etc/supervisor/conf.d/molo.conf
COPY docker/supervisord.conf /etc/supervisord.conf

EXPOSE 8000

CMD ["docker-start.sh"]

RUN pip install -r pip-freeze.txt && \
    npm install -g less coffee-script && \
    django-admin collectstatic --noinput &&\
    USE_DEFAULT_CACHE=True django-admin compress
