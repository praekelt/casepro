FROM praekeltfoundation/django-bootstrap:py2

RUN apt-get-install.sh git nodejs npm redis-server && \
    ln -s /usr/bin/nodejs /usr/bin/node

RUN npm install -g less coffee-script

COPY pip-freeze.txt .
RUN pip install -r pip-freeze.txt
RUN pip install supervisor

COPY . /app
RUN pip install -e .

ENV DJANGO_SETTINGS_MODULE "casepro.settings_production"

RUN mkdir -p /app/media \
             /etc/supervisor/conf.d/ \
             /var/log/supervisor

COPY docker/supervisor.conf /etc/supervisor/conf.d/casepro.conf
COPY docker/supervisord.conf /etc/supervisord.conf

RUN sed -ie 's|/static/|/sitestatic/|g' /etc/nginx/conf.d/django.conf

CMD ["supervisord", "-c", "/etc/supervisord.conf"]

RUN django-admin collectstatic --noinput && \
    USE_DEFAULT_CACHE=True django-admin compress
