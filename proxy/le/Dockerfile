FROM nginxproxy/acme-companion:2.2.1
RUN apk update && apk upgrade
ARG DOCKER_GEN_VERSION
ENV DOCKER_GEN_VERSION=${DOCKER_GEN_VERSION}
COPY ./docker-gen /usr/local/bin/
