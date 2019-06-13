# JupyterHub Share Link

This is a new project that is still a work in progress. Please do not attempt to
use it in production yet. Contributors welcome!

## Try it

1. Start JupyterHub using the configuration in this repo.
2. Log in with any username and password. (The ``DummyAuthenticator`` is used by
   this demo configuration.)
3. Create and save a notebook to share.
4. Open a separate browser and log in to the hub as a different user.
5. ``GET`` the following URL:

   ```
   /services/share-link/{source_user}/{source_server_name}/{source_image_name}/{path}
   ```
6. The user will have a new server started running the same image as User A, and
   the notebook will be copied and opened.

## TODO

* Clean up base url hack.
* Fix up ``dest_path`` default, which should take the filename not the full
  source path.
* Reuse an existing server if it has the right "profile" / image.
* Add URL For *creating* share links. Can servers be made to know which image
  they are running?
* Add link expiration time.
* Add utility CLI for generating keys using ``cryptography``.
* Sign with JWT to ensure recipient cannot tamper with path or time.
* Possibly encrypt path so that directory structure is not leaked to recipient.
