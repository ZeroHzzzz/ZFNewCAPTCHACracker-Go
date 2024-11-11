# start with a base image
FROM ubuntu:20.04

# install dependencies
RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list &&\
	apt update && \ 
	apt install -y nginx supervisor && \
	apt install -y python3 python3-dev python3-pip python3-virtualenv python3-opencv python3-matplotlib  python3-scipy python3-skimage && \
	pip install uwsgi numpy Flask requests -i https://mirrors.ustc.edu.cn/pypi/web/simple && \
	apt-get purge -y --auto-remove python3-pip &&\
	rm -rf /var/lib/apt/lists/*

# update working directories
COPY ./app /app
COPY ./config /config

# setup config
RUN echo "\ndaemon off;" >> /etc/nginx/nginx.conf && \
	rm /etc/nginx/sites-enabled/default && \
	ln -s /config/nginx.conf /etc/nginx/sites-enabled/ && \
	ln -s /config/supervisor.conf /etc/supervisor/conf.d/

EXPOSE 80
CMD ["supervisord"]
