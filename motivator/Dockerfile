FROM python:3.7-alpine

ENV PYTHONUNBUFFERED=0

ENV DJANGO_SETTINGS_MODULE=motivator.settings.development

RUN apk add --no-cache --virtual build-deps curl gcc g++ make postgresql-dev postgresql-client bash

RUN mkdir /motivator

WORKDIR /motivator

ADD . /motivator

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
