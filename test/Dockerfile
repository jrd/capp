# syntax=docker/dockerfile:1
FROM debian:12
VOLUME /var/lib/docker
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y ca-certificates curl gnupg \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
 && chmod a+r /etc/apt/keyrings/docker.gpg \
 && echo deb \
    "[arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg]" \
    https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") \
    stable \
    > /etc/apt/sources.list.d/docker.list \
 && apt-get update
RUN apt-get install -y \
        containerd.io \
        curl \
        docker-buildx-plugin \
        docker-ce \
        docker-ce-cli \
        docker-compose-plugin \
        python3 \
        python3-yaml \
        ssh \
        sudo \
        systemd \
        tmux \
        vim
RUN sed -ri '/#PermitRootLogin/a PermitRootLogin yes\n' /etc/ssh/sshd_config \
 && echo 'root:root' | chpasswd
COPY capp-installer /root/capp-installer
COPY docker-entrypoint /usr/local/bin/docker-entrypoint
EXPOSE 22
EXPOSE 122
EXPOSE 80
EXPOSE 443
ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
