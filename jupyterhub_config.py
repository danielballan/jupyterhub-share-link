import os
import sys

import dockerspawner


c.JupyterHub.services = [
    {
        'name': 'share-link',
        'admin': True,
        'url': 'http://127.0.0.1:21211',
        'command': [sys.executable, '-m', 'jupyterhub_share_link.run'],
    }
]


class PatchedDockerSpawner(dockerspawner.DockerSpawner):
    # We need the server to know what image it is using.
    # The KubeSpawner already does this, added in
    # https://github.com/jupyterhub/kubespawner/pull/193
    def get_env(self):
        env = super().get_env()
        env['JUPYTER_IMAGE_SPEC'] = self.image
        return env


c.JupyterHub.spawner_class = PatchedDockerSpawner
c.DockerSpawner.remove_containers = True
c.DockerSpawner.image_whitelist = {
    'base': 'danielballan/base-notebook-with-image-spec-extension',
    'scipy': 'danielballan/scipy-notebook-with-image-spec-extension',
}
c.JupyterHub.allow_named_servers = True
c.DockerSpawner.name_template = "{prefix}-{username}-{servername}"

c.Spawner.default_url = '/lab'

# The docker instances need access to the Hub,
# so the default loopback port doesn't work:
from jupyter_client.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]

c.JupyterHub.authenticator_class = 'jupyterhub.auth.DummyAuthenticator'

# HACK? Workaround. See jupyterhub.handlers.base "don't own".
c.JupyterHub.admin_access = True
