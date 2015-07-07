FROM microservice_python
MAINTAINER Cerebro <cerebro@ganymede.eu>

ADD ./ /opt/armada-bind
ADD ./supervisor/armada-bind.conf /etc/supervisor/conf.d/

ENV PYTHONPATH /opt/microservice/src/local_magellan:/opt/microservice_python/src

EXPOSE 80
