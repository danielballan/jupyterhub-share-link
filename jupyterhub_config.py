import os
import sys

c.JupyterHub.services = [
    {
        'name': 'share-link',
        'admin': True,
        'url': 'http://127.0.0.1:21211',
        'command': [sys.executable, '-m', 'jupyterhub_share_link.run'],
    }
]

c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'
c.DockerSpawner.remove_containers = True
c.DockerSpawner.image_whitelist = {
    'base': 'jupyter/base-notebook',
    'scipy': 'jupyter/scipy-notebook'}
c.JupyterHub.allow_named_servers = True
c.DockerSpawner.name_template = "{prefix}-{username}-{servername}"

# The docker instances need access to the Hub,
# so the default loopback port doesn't work:
from jupyter_client.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]

c.JupyterHub.authenticator_class = 'jupyterhub.auth.DummyAuthenticator'

# HACK? Workaround. See jupyterhub.handlers.base "don't own".
c.JupyterHub.admin_access = True
