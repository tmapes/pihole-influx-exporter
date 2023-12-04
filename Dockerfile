FROM python:3.11.6-alpine3.18

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