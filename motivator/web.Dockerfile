FROM python:3.7-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk add --no-cache --virtual build-deps curl gcc g++ make postgresql-dev postgresql-client bash jpeg-dev freetype-dev zlib-dev

RUN mkdir /motivator

WORKDIR /motivator

ADD . /motivator

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./deployment.sh /usr/local/bin/deployment.sh

RUN chmod 777 /usr/local/bin/deployment.sh

CMD /usr/local/bin/deployment.sh