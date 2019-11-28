Installation
------------

Install [compose-dirs](https://github.com/jrd/compose-systemd)

Use the following config:

    compose_dir=/etc/compose
    compose_user=compose
    tmpl_name=compose
    deps_file=compose.deps

Create a `deploy` account without any password (login only allowed with private keys).

Add `compose` user to the `deploy` group (for allowing it to see deployed files).

Adjust `compose` user sudoer file:

    # Allow members of compose group to execute compose-dirs command
    Cmnd_Alias COMPOSE_DIRS = /usr/local/bin/compose-dirs
    Cmnd_Alias COMPOSE_SVC = /usr/bin/systemctl start compose@*, /usr/bin/systemctl stop compose@*, /usr/bin/systemctl restart compose@*
    %compose   ALL= NOPASSWD: COMPOSE_DIRS, COMPOSE_SVC

Install `deploy` and `undeploy` script in `/usr/local/bin`.

Usage
-----

All actions should be done under the **`compose`** account.

### Deploy

`compose@host $ deploy ~deploy/dca/PATH_TO_DCA_FILE.dca [clean] [nostart]`

This will verify the file, extract it, install docker images, docker-compose config file, systemd service and start it.  
If `clean` is provided, any pre-existing volumes will be deleted prior deploy.  
If `nostart` is provided, the system service will not be started. This let you the chance to hack into before starting it.

This will exit with `0` status if deploy was ok, greater number in case of error.

### Undeploy

`compose@host $ undeploy APP TARGET_ENV [all]`

This will stop the docker services, remove the systemd service, delete docker-compose files and images.  
If `all` is provided, then all related images and volumes will also be deleted.  
Be careful, volumes may contains data not backuped!

This will exit with `0` status if undeploy was ok, greater number in case of error.

### Start, Restart, Stop

Any docker compose application is deployed as a **systemd service**, so it can be monitored with usual tools.

For a **myapp** app, deployed on a **prod** environment, here are the actions that can be done:

    compose@host $ systemctl status compose@myapp-prod
    compose@host $ sudo systemctl start compose@myapp-prod
    compose@host $ sudo systemctl restart compose@myapp-prod
    compose@host $ sudo systemctl stop compose@myapp-prod


### Hacking

Go into you app and environment folder, containing `docker-compose.yml` file.  
For instance `cd myapp/prod`.

Then use any `docker-compose` command, like `exec` to enter a container.

⚠ Keep it mind that the compose app is handled by a systemd service so **don't start or stop** the compose while the service is running or use `systemctl` commands.

### Logging

Access logging by:

- using `docker-compose logs` command.
- using `journalctl -feu compose@myapp-env` command.

License and authors
-------------------

[MIT](https://choosealicense.com/licenses/mit/)

Authors:

- Cyrille Pontvieux
- David Garceries
