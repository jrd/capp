CHANGELOG
=========

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
