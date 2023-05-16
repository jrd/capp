FROM alpine:3.18
ARG DOCKER_GEN_VERSION
ENV DOCKER_GEN_VERSION=${DOCKER_GEN_VERSION} \
    DOCKER_HOST=unix:///tmp/docker.sock \
    NGINX_PROXY_CONTAINER=nginx-proxy
# Install packages required by the image
RUN apk update && \
    apk upgrade && \
    apk add --no-cache --virtual \
        .bin-deps \
        openssl \
        nginx \
        docker-cli && \
    mkdir -p /run/nginx /etc/nginx/conf.d
COPY ./LICENSE /usr/local/share/doc/docker-gen/
COPY ./docker-gen /usr/local/bin/
COPY ./docker-gen-wrapper /usr/local/bin/
COPY ./check_and_notify /usr/local/bin/
COPY ./nginx.conf /etc/nginx/
COPY ./nginx.tmpl /etc/docker-gen/templates/
ENTRYPOINT ["/usr/local/bin/docker-gen-wrapper"]
CMD ["-notify", "/usr/local/bin/check_and_notify", "-watch", "-wait", "5s:30s", "/etc/docker-gen/templates/nginx.tmpl", "/etc/nginx/conf.d/default.conf"]
