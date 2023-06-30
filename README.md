Prerequisite
------------

The following binaries should be available:
- useradd
- usermod
- base64
- curl
- docker, docker compose OR docker-compose
- python3
- python3-yaml
- sudo
- tar
- unxz

The scripts rely on a system running **systemd**.

Installation
------------

- Create the installer: `make installer`
- Copy the `capp-installer` file to your host target.
- Execute it with **root privilege** and by specifying the **default hostname** and **email address** to use for the `proxy` (email is used for *let's encrypt*):  
`capp-installer example.com user@example.com`

Be sure to have your `sshd` service up and running.

Configuration
-------------

Users allowed to upload [*DCA*](https://github.com/jrd/dca_format) files should have their public keys in `/etc/dca-authorized-keys`.

Users allowed to act on deployments should have their public keys in `/etc/deploy-authorized-keys`.

You don't have to do anything after modifying this file for the content to be taken into account.

Admin usage
-----------

All actions should be done under the **`compose`** account.

To switch to it, use `su -s /bin/bash --login compose` from `root` account.

Main scripts are `compose-dirs` and `capp`.

Usage
-----

Two ssh servers are running on the node: one for administration and deployements (port 22), one for transfering *Docker Compose Archives* (port 122).

### Transfering a DCA and its signature

If you have your public key allowed, you could transfer a *dca* file and its signature to *node* by doing something like:

`scp -P 122 my.dca* dca@node:`

### Check upload ok

`ssh deploy@node dcas [check]`

Without `check`, it will only list *dca* files. With it, it will also indicate if checksum is ok or not.

### Deploy

`ssh deploy@node deploy /home/deploy/dca/my.dca [clean] [nostart]`

This will verify the file, extract it, install docker images, docker-compose config file, systemd service and start it.  
If `clean` is provided, any pre-existing volumes will be deleted prior deploy.  
If `nostart` is provided, the system service will not be started. This let you the chance to hack into before starting it.

This will exit with `0` status if deploy was ok, greater number in case of error.

### Undeploy

`ssh deploy@node undeploy my_app integ [all]`

This will stop the docker services, remove the systemd service, delete docker-compose files and images.  
If `all` is provided, then all related images and volumes will also be deleted.  
Be careful, volumes may contains data not backuped!

This will exit with `0` status if undeploy was ok, greater number in case of error.

### Apps, Start, Restart, Stop, Status, Logs

See `ssh deploy@node help` for an exhaustive list of all actions and options.

### Exec-ing into containers

Be sure to force a TTY with ssh: `ssh -t` or `RequestTTY yes` in `.ssh/config`.

`sshi -t deploy@node exec my_app integ my_service`

### Hack for admin

- Connect into *node* and change to the `compose` account (or your account if in the `docker` group).
- Go into you app and environment folder, containing `docker-compose.yml` file, for instance `cd myapp/prod` from `compose` home dir.
- Use any `docker compose` command, like `exec` to enter a container.

⚠ Keep in mind that the compose app is handled by a systemd service so **don't start or stop** the compose while the service is running.  
Better use the `capp start|stop` commands or `sudo systemctl start|stop` commands.

License and authors
-------------------

[MIT](./LICENSE)

Authors:

- Cyrille Pontvieux
- David Garceries
- Samir Hachimi
