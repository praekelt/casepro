FROM praekeltfoundation/django-bootstrap:py3.6-jessie
RUN apt-get-install.sh git \
    redis-server supervisor libpq-dev gcc && \
    ln -s /usr/bin/nodejs /usr/bin/node

#Upgrade Nodejs to v4.9 as the current version v4.6 doesn't appear to have support for object.assign 
#Check https://node.green for compatibility
RUN apt-get update
RUN apt-get install curl -y
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash
RUN apt-get install nodejs -y


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

COPY . /app
RUN pip install -e . &&\
pip install -r pip-freeze.txt &&\
pip install -r pip-freeze-praekelt.txt &&\
npm install -g less coffee-script &&\
django-admin collectstatic --noinput &&\  
USE_DEFAULT_CACHE=True django-admin compress
