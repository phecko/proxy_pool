FROM phecko/scrapy:0.1

COPY requirements.txt  /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

COPY supervisord.conf /etc/supervisord.conf
COPY supervisor/ /etc/supervisor/
COPY docker-entrypoint.sh /docker-entrypoint.sh

VOLUME /data/logs


ENTRYPOINT ["/docker-entrypoint.sh"]
