# JupyterHub Share Link

This is a new project that is still a work in progress. Please do not attempt to
use it in production yet. Contributors welcome!

## Demo

In this GIF, Alice logs in, right-clicks a notebook and chooses "Copy Shareable
Link". A dialog box appears, saying:

> For the next hour, any other user on this JupyterHub who has this link will be
> able to fetch a copy of your latest saved version of
> dask-examples/array.ipynb.

She copies the link and gives it to Bob. Then, on the right, Bob logs in and
pastes the link into his browser. He is given a copy of Alice's notebook.

![Demo](https://github.com/danielballan/jupyterhub-share-link/blob/master/demo.gif?raw=true)

## JupyterHub Compatibility

* jupyterhub-share-link v0.0.1 is compatible with JupyterHub 1.0
* juptyerhub-share-link v0.1.x takes a different approach that requires a
  [one-line change](https://github.com/jupyterhub/jupyterhub/pull/2755) to
  jupyterhub itself, which has been submitted for consideration for inclusion in
  jupyterhub

## Uses and Limitations

This is for low-effort, short-term sharing between users who are on the same
Hub.

The sender right-clicks a notebook (or any file) and clicks "Copy Shareable
Link." The sender gives that link to any other user on the same Hub. When
another user clicks the share link, the last saved version of the file is copied
from the sender's notebook server to the recipient's. If the sender changes the
file, the recipient can click the link again to make another copy reflecting the
changes. After a given time interval, the link expires.

On Hubs that provide the user with options at spawn time, such as a
container-based spawner, the share link encodes both the notebook and the
options (e.g. the container image) that the sender was running that notebook in.
The recipient will automatically be directed to a server spawned with the same
options: the service finds a suitable existing one or spawns one if necessary.
Thus the recipient has some assurance that they will be running the notebook in
a compatible software environment.

This approach is not suitable for persistent sharing, such as galleries or lists
of links to be maintained long term. For those use cases, it is better to encode
software dependencies (as in a Binder repo) rather than relying on the
availability of a specific image.

## Try it &mdash; with containers or without containers

This approach should be compatible with any spawner. Two examples are given
here, a local process spawner and a container-based spawner.

### With Containers

1. Install using pip.

    ```
    pip install jupyterhub-share-link
    ```

2. Install [DockerSpawner](https://github.com/jupyterhub/dockerspawner).

    ```
    pip install dockerspawner
    ```

3. Generate a key pair that will be used to sign and verify share links.

    ```
    # creates private.pem and public.pem in the current directory
    python -m jupyterhub_share_link.generate_keys
    ```

4. Start JupyterHub using an example configuration provided in this repo.

    ```
    jupyterhub -f example_config_dockerspawner.py
    ```

5. Log in with any username and password---for example, ``alice``.
   (The ``DummyAuthenticator`` is used by this demo configuration.)

6. Spawn a server using the default image,
   ``danielballan/base-notebook-with-image-spec-extension``.

7. Create and save a notebook ``Untitled.ipynb`` to share.

8. Find ``Untitled.ipynb`` in the file browser and right-click it.
   A dialog box will appear. Click the button to copy the link.

9. Log in as a different user and paste the shared link.

10. The user will have a new server started running the same image as ``alice``,
    and the notebook will be copied and opened.

### Without Containers

1. Install using pip.

    ```
    pip install jupyterhub-share-link
    ```

2. Generate a key pair that will be used to sign and verify share links.

    ```
    # creates private.pem and public.pem in the current directory
    python -m jupyterhub_share_link.generate_keys
    ```

3. Install the labextension into the user environment.

    ```
    # Disable the default share-file extension and register our custom one.
    jupyter labextension disable @jupyterlab/filebrowser-extension:share-file
    jupyter labextension install jupyterhub-share-link-labextension
    ```

4. Start JupyterHub using an example configuration provided in this repo. (In
   order to be able to log in as multiple users, you will likely need to run
   this as root.)

    ```
    jupyterhub -f example_config_no_containers.py
    ```

5. Log in as a system user and start the user's server.

6. Create and save a notebook ``Untitled.ipynb`` to share.

7. Find ``Untitled.ipynb`` in the file browser and right-click it.
   A dialog box will appear. Click the button to copy the link.

8. Log in as a different user and paste the shared link.

9. The notebook will be copied to that user's server and opened.

## Design

This involves:

* A stateless Hub Service (in this repository) with the routes:

  ```
  POST /create  # issue a shareable link
  GET /open  # open a shared link
  GET /  # verion info
  ```
* A public/private key pair that belong to the service, enabling it issue
  "share" links that it can verify the recipient has not tampered with.
* A labextension that customizes the behavior of the 'Copy Share Link' context
  menu item, stored at
  [danielballan/jupyterhub-share-link-labextension](https://github.com/danielballan/jupyterhub-share-link-labextension).

The file-copying occurs via the notebook's ContentsManager, so there is no need
for users to be on the same filesystem. They only have to be on the same Hub.

## Open Questions

* Encrypt path so that directory structure is not leaked to recipient?
