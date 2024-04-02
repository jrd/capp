FROM registry.gitlab.com/systra/qeto/infra/certbot-companion:1.0.1
RUN apk update && apk upgrade
ARG DOCKER_GEN_VERSION
ENV DOCKER_GEN_VERSION=${DOCKER_GEN_VERSION}
COPY ./docker-gen /usr/local/bin/
