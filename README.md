Installation
------------

Install [compose-dirs](https://github.com/jrd/compose-systemd)

Use the following config:
```
compose_dir=/etc/compose
compose_user=compose
tmpl_name=compose
deps_file=compose.deps
```

Create a `deploy` account without any password (login only allowed with private keys).

Add `compose` user to the `deploy` group (for allowing it to see deployed files).

Adjust `compose` user sudoer file:
```
# Allow members of compose group to execute compose-dirs command
Cmnd_Alias COMPOSE_DIRS = /usr/local/bin/compose-dirs
Cmnd_Alias COMPOSE_SVC = /usr/bin/systemctl start compose@*, /usr/bin/systemctl stop compose@*, /usr/bin/systemctl restart compose@*
%compose   ALL= NOPASSWD: COMPOSE_DIRS, COMPOSE_SVC
```

Install `deploy` and `undeploy` script in `/usr/local/bin`.

Usage
-----

`deploy PATH_TO_DCA_FILE.dca`

This will verify the file, extract it, install docker images, docker-compose config file, systemd service and start it

The opposite:

`undeploy APP TARGET_ENV [all]`

This will stop the docker services, remove the systemd service, delete docker-compose files and images.

If `all` is provided, then all related images and volumes will also be deleted. Be careful, volumes may content data you forgot to backup!
