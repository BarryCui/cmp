FROM centos:7

LABEL maintainer="cuizhisong@icicle.com"
# set charset
ENV LANG en_US.UTF-8
# set up azure
RUN yum install -y python3 \
    && python3 -m pip install -U pip \
    && rpm --import https://packages.microsoft.com/keys/microsoft.asc \
    && sh -c 'echo -e "[azure-cli] \n\
name=Azure CLI \n\
baseurl=https://packages.microsoft.com/yumrepos/azure-cli \n\
enabled=1 \n\
gpgcheck=1 \n\
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/azure-cli.repo' \
    && yum install azure-cli -y 
# copy needed files
COPY . .
# install python dependencies and set up supervisor config
RUN pip3 install -i https://pypi.doubanio.com/simple/ -r requirements.txt \
    && sh -c 'echo -e "[supervisord] \n\
logfile = /tmp/supervisord.log \n\
logfile_maxbytes = 50MB \n\
logfile_backups=10 \n\
loglevel = info \n\
pidfile = /tmp/supervisord.pid \n\
nodaemon = true \n\
minfds = 1024 \n\
minprocs = 200 \n\
umask = 022 \n\
user = root \n\
identifier = supervisor \n\
directory = /tmp \n\
nocleanup = true \n\
childlogdir = /tmp \n\
strip_ansi = false \n\
[program:celery] \n\
command=celery -A cmp.celery worker \n\
startsecs=60 \n\
startretries=5 \n\
stdout_logfile=/tmp/celery.log \n\
stderr_logfile=/tmp/celery_err.log \n\
[program:gunicorn] \n\
command=gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app \n\
startsecs=60 \n\
startretries=5 \n\
stdout_logfile=/tmp/gunicorn.log \n\
stderr_logfile=/tmp/gunicorn_err.log" >> /etc/supervisord.conf'

EXPOSE 8000
# start supervisor
ENTRYPOINT ["supervisord", "-n", "-c", "/etc/supervisord.conf"]
