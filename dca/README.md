How to add a user
-----------------

- Put his/her public key on a new line into `users-keys` file. Be sure to finish the public key with a meaningful name.
- Restart the service: `sudo systemctl restart compose@dca`

You can add multiple public keys for a user if necessary.

How to remove a user
--------------------
- Remove the corresponding public key from `users-keys` file.
- Restart the service: `sudo systemctl restart compose@dca`
