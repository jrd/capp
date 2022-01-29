CHANGELOG
=========

version 2.6.1
-------------
- Fix `rmdir` that was too soon in the installer
- Updated image versions (`le-gen` still need an still-unreleased upgraded version).

version 2.6.0
-------------
- Updated image versions.
- `capp` can be tested in docker.
- `compose-dirs` updated to version `1.4.0`.
- More verbose tasks on `deploy`/`undeploy`.

version 2.5.0
-------------
- Do not use cache when using `build` command.
- Fix `undeploy` command on non-existant app/env.
- Fix parsing metadata version on `undeploy`.

version 2.4.0
-------------
- `build` command to force build and pull application services.
- better `exec` command, with multiple arguments supported and you can inject environment variables, change the working directory or the current user.

version 2.3.1
-------------
- Let’s encrypt companion update

version 2.3.0
-------------
- Security updates (docker images)
- Support for multiple (ssh) keys per user (`listkey`, `addkey`, `delkey`)
- Support for `exec` action to enter an application service

version 2.2.0
-------------
- Rights and user management
- Generate `authorized_keys` on login attempt
- Updated docker versions
- Pull images on deploy
- `/etc/capp/le_blacklist.txt` file to list host that should NOT be processed by Let's Encrypt

version 2.1.0
-------------
- Usage of `verify_dca.py` in `capp`.
- Hash check on deploy is now a bit quicker and use less memory
- Hooks on deploy/undeploy action
- Fix Hooks invocation (as-root, string-only parameters)

version 2.0.0
-------------
- DCA format version 2
