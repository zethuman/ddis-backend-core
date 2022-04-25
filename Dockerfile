FROM registry.gitlab.com/d6763/backend-core:base

WORKDIR /usr/src/ddis-backend-core

COPY / /usr/src/ddis-backend-core

RUN python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del .tmp-build-deps 

EXPOSE 4020