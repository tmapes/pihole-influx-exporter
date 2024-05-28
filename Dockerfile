FROM python:3.12.3-alpine3.18@sha256:24680ddf8422899b24756d62b31eb5de782fbb42e9c2bb1c70f1f55fcf891721

# install dumb-init
RUN wget -qO /usr/local/bin/dumb-init https://binrepo.mapes.info/repository/github/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64 \
    && chmod +x /usr/local/bin/dumb-init \
    && mkdir -p /opt/pihole-metrics

# move required files
COPY * /opt/pihole-metrics

# install dependencies
RUN pip install -r /opt/pihole-metrics/requirements.txt

# update our cron tab to run the script every minute
RUN echo "*/1 * * * * /opt/pihole-metrics/main.py" | crontab -

ENTRYPOINT [ "/usr/local/bin/dumb-init", "--" ]
CMD ["/usr/sbin/crond", "-f"]