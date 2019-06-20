# JupyterHub Share Link

This is a new project that is still a work in progress. Please do not attempt to
use it in production yet. Contributors welcome!

## Uses and Limitations

This is for low-effort, short-term sharing between users who are on the same
Hub.

The sender click a button to create a "share link" for a notebook and then gives
that link to any other user on the same Hub. When another user clicks the share
link, the last saved version of the file is copied from the sender's notebook server to
the recipient's. If the sender changes the file, the recipient can click the
link again to make another copy reflecting the changes. After a given time
interval, the link expires.

On Hubs using a container-based spawner, the share link encodes both the
notebook and the *container image* that the sender was running that notebook in.
The recipient will automatically be directed to a server running that same
container image, and thus have some assurance that they will be running the
notebook in a compatible software environment. (This is not the case when
sharing notebooks via email or Dropbox.)

This approach is not suitable for persistent sharing, such as galleries or lists
of links to be maintained long term. For those use cases, it is better to encode
software dependencies (as in a Binder repo) rather than relying on the
availability of a specific image.

## Try it

This demonstrates sharing with a container-based spawner, but this can also be
used with a simple local process spawner or any other spawner.

1. Clone this repository and install its requirements.

    ```
    git clone https://github.com/danielballan/jupyterhub-share-link
    cd jupyterhub-share-link
    pip install -r requirements.txt
    ```
2. Generate a key pair that will be used to sign and verify share links.

    ```
    # creates private.pem and public.pem in the current directory
    python -m jupyterhub_share_link.generate_keys
    ```
3. Start JupyterHub using the example configuration in this repo.

    ```
    jupyterhub  # uses jupyterhub_config.py in current directory
    ```

4. Log in with any username and password---for example, ``alice``.
   (The ``DummyAuthenticator`` is used by this demo configuration.)

5. Spawn a server using the default image,
   ``danielballan/base-notebook-with-image-spec-extension``.

6. Create and save a notebook ``Untitled.ipynb`` to share.

7. Click the share button, the paper airplane icon on the left side of the
   notebook toolbar. Click the button to copy the link.

8. Log in as a different user and paste the shared link.

9. The user will have a new server started running the same image as ``alice``,
   and the notebook will be copied and opened.

## Design

This involves:

* A stateless Hub Service (this repo) with the routes:

  ```
  POST /create
  POST /open
  ```
* A public/private key pair that belong to the service, enabling to verify that
  shared links are valid.
* A small notebook server extension for exposing ``JUPYTER_IMAGE_SPEC``, an
  environment variable in a new server REST endpoint.
  https://github.com/danielballan/jupyter-expose-image-spec
* A labextension that adds button to the notebook toolbar.
  https://github.com/danielballan/jupyterhub-share-link-labextension

## Open Questions

* Encrypt path so that directory structure is not leaked to recipient?
* If senders server has stopped, do we temporarily start one? Probably not.
