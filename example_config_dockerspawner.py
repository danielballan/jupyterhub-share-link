import dockerspawner
from jupyter_client.localinterfaces import public_ips
from traitlets.config import get_config
import sys


c = get_config()
c.JupyterHub.services = [
    {
        'name': 'share-link',
        'admin': True,
        'url': 'http://127.0.0.1:21211',
        'command': [sys.executable, '-m', 'jupyterhub_share_link.run'],
    }
]
c.JupyterHub.admin_access = True  # Service needs to access user servers.

c.JupyterHub.allow_named_servers = True
c.Spawner.cmd = ['jupyter-labhub']

c.JupyterHub.authenticator_class = 'jupyterhub.auth.DummyAuthenticator'


c.JupyterHub.spawner_class = dockerspawner.DockerSpawner
c.DockerSpawner.remove_containers = True
c.DockerSpawner.image_whitelist = [
    'danielballan/base-notebook-with-jupyterhub-share-labextension',
    'danielballan/scipy-notebook-with-jupyterhub-share-labextension',
]

# This is only needed until
# https://github.com/jupyterhub/dockerspawner/pull/315
# is merged and released.
c.DockerSpawner.name_template = "{prefix}-{username}-{servername}"

c.Spawner.default_url = '/lab'

# The docker instances need access to the Hub,
# so the default loopback port doesn't work:
c.JupyterHub.hub_ip = public_ips()[0]
