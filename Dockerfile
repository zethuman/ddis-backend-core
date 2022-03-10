FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /usr/src/ddis-backend-core

COPY / /usr/src/ddis-backend-core

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers

RUN python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del .tmp-build-deps 

EXPOSE 4020