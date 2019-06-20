"""An example service authenticating with the Hub.
This serves `/services/whoami/`, authenticated with the Hub, showing the user their own info.
"""
import base64
from datetime import datetime, timedelta
from getpass import getuser
import json
import os
import pathlib
import uuid

import jwt
from jupyterhub.services.auth import HubAuthenticated
from jupyterhub.utils import url_path_join
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import authenticated
from tornado.web import RequestHandler
from tornado.web import HTTPError
from urllib.parse import urlparse, quote as urlquote

from .launcher import Launcher


HubAuthenticated.hub_auth

private_key = pathlib.Path("private.pem").read_text()
public_key = pathlib.Path("public.pem").read_text()


class CreateSharedLink(HubAuthenticated, RequestHandler):
    @authenticated
    async def post(self):
        data = json.loads(self.request.body.decode('utf-8'))

        now = datetime.utcnow()
        if data.get('expiration_time') is not None:
            expiration_time = datetime.fromtimestamp(data['expiration_time'])
        else:
            # Default to one hour lifetime.
            expiration_time = now + timedelta(hours=1)
        # Enforce a max of two days.
        # This is not for long-term sharing, galleries, etc.
        max_time = now + timedelta(days=2)
        if expiration_time > max_time:
            raise HTTPError(
                403, (f"expiration_time must no more than two days "
                      f"from now (current max: {max_time.timestamp()})")
            )

        payload = {
            'user': self.get_current_user()['name'],
            'image': data['image'],
            'path': data['path'],
            'server_name': data.get('server_name', ''),
            'exp': expiration_time
        }
        token = jwt.encode(payload, private_key, algorithm="RS256")
        base64_token = base64.urlsafe_b64encode(token)
        base_url = f'{self.request.protocol}://{self.request.host}'
        link = url_path_join(base_url,
                             os.getenv('JUPYTERHUB_SERVICE_PREFIX'),
                             f'open?token={base64_token.decode()}')
        self.write({'link': link})


class OpenSharedLink(HubAuthenticated, RequestHandler):
    @authenticated
    async def get(self):
        unverified_base64_token = self.get_argument('token')
        unverified_token = base64.urlsafe_b64decode(unverified_base64_token)
        try:
            token = jwt.decode(unverified_token, public_key, algorithms='RS256')
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPError(
                403, "Sharing link has expired. Ask for a fresh link."
            )
        except jwt.exceptions.InvalidSignatureError:
            raise HTTPError(
                403, ("Sharing link has an invalid signature. Was it "
                      "copy/pasted in full?")
            )

        source_username = token['user']
        source_server_name = token['server_name']
        image = token['image']
        source_path = token['path']
        dest_path = self.get_argument('dest_path',
                                      os.path.basename(source_path))

        current_user = self.get_current_user()
        launcher = Launcher(current_user, self.hub_auth.api_token)

        # HACK
        # The Jupyter Hub API only gives us a *relative* path to the user
        # servers. Use self.request to get at the public proxy URL.
        base_url = f'{self.request.protocol}://{self.request.host}'
        headers = {'Authorization': f'token {launcher.hub_api_token}'}

        # Ensure destination has a server to share into.
        # First check to see if any of the currently-running servers have the
        # same container image as the one we need.
        resp = await launcher.api_request(
            url_path_join('users', current_user['name']),
            method='GET',
        )
        dest_user_data = json.loads(resp.body.decode('utf-8'))
        for server in (dest_user_data['servers'] or {}).values():
            image_spec_url = url_path_join(base_url,
                                           server['url'],
                                           'image-spec')
            req = HTTPRequest(image_spec_url, headers=headers)
            resp = await AsyncHTTPClient().fetch(req)
            this_image = json.loads(resp.body.decode('utf-8')).get('JUPYTER_IMAGE_SPEC')
            if this_image == image:
                dest_server_name = server['name']
                result = server
                break
        else:
            # No currently-running server has the container image we need.
            # Start a new server with a random name.
            dest_server_name = f'shared-link-{str(uuid.uuid4())[:8]}'
            result = await launcher.launch(image, dest_server_name)

            if result['status'] == 'pending':
                redirect_url = f"{result['url']}?next={urlquote(self.request.full_url())}"
                # Redirect to progress bar, and then back here to try again.
                self.redirect(redirect_url)
            assert result['status'] == 'running'

        # Fetch the content we want to copy.
        resp = await launcher.api_request(
            url_path_join('users', source_username),
            method='GET',
        )
        source_user_data = json.loads(resp.body.decode('utf-8'))
        source_server_url = source_user_data['servers'][source_server_name]['url']
        content_url = url_path_join(base_url,
                                    source_server_url,
                                    'api/contents',
                                    source_path)
        headers = {'Authorization': f'token {launcher.hub_api_token}'}
        req = HTTPRequest(content_url, headers=headers)
        resp = await AsyncHTTPClient().fetch(req)
        content = resp.body

        # Copy content into destination server.
        to_username = launcher.user['name']
        dest_url = url_path_join(base_url,
                                 'user',
                                 to_username,
                                 dest_server_name,
                                 'api/contents/',
                                 dest_path)
        req = HTTPRequest(dest_url, "PUT", headers=headers, body=content)
        resp = await AsyncHTTPClient().fetch(req)

        redirect_url = url_path_join(result['url'], 'lab', 'tree', dest_path)

        # necessary?
        redirect_url = redirect_url if redirect_url.startswith('/') else '/' + redirect_url

        self.redirect(redirect_url)


def main():
    app = Application(
        [
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + r'create/?', CreateSharedLink),
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + r'open/?', OpenSharedLink)
        ]
    )

    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    http_server.listen(url.port, url.hostname)

    IOLoop.current().start()


main()
