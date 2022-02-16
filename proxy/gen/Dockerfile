FROM jwilder/docker-gen:0.8.2
RUN apk update && apk upgrade && \
    apk add nginx && \
    mkdir -p /run/nginx
COPY ./docker-gen-wrapper /usr/local/bin/
COPY ./check_and_notify /usr/local/bin/
COPY ./nginx.tmpl /etc/docker-gen/templates/nginx.tmpl
ENTRYPOINT ["/usr/local/bin/docker-gen-wrapper"]
ENV NGINX_PROXY_CONTAINER=nginx-proxy
CMD ["-notify", "/usr/local/bin/check_and_notify", "-watch", "-wait", "5s:30s", "/etc/docker-gen/templates/nginx.tmpl", "/etc/nginx/conf.d/default.conf"]
