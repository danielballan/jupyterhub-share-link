# JupyterHub Share Link

This is a new project that is still a work in progress. Please do not attempt to
use it in production yet. Contributors welcome!

## Uses and Limitations

Produce a "share link" for a notebook (or any file) and give it to other users
on your Hub. When another user clicks the share link, the current version of
the file is copied from your notebook server to theirs. If you change the file,
the recipient can click the link again to make another copy reflecting the
changes. After a given time interval, the link expires.

This is for low-effort, short-term sharing between users who are on the same Hub
using a container-based spawner. The share link encodes both the notebook and
the *container image* that the sender was running that notebook in. The
recipient will automatically be directed to a server running that same container
image, and thus have some assurance that they will be running the notebook in a
compatible software environment. (This is not the case when sharing notebooks
via email or Dropbox.)

This approach is not suitable for persistent sharing, such as galleries or lists
of links to be maintained long term. For those use cases, it is better to encode
software dependencies (as in a Binder repo) rather than relying on the
availability of a specific image.

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

* Add URL For *creating* share links. Can servers be made to know which image
  they are running?
* Reuse an existing server for the destination if it has the right "profile" /
  image.
* Add link expiration time.
* Add utility CLI for generating keys using ``cryptography``.
* Sign with JWT to ensure recipient cannot tamper with path or time.

## Open Questions

* Encrypt path so that directory structure is not leaked to recipient?
* If senders server has stopped, do we temporarily start one? Probably not.
