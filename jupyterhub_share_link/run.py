"""An example service authenticating with the Hub.
This serves `/services/whoami/`, authenticated with the Hub, showing the user their own info.
"""
import json
import os
from getpass import getuser
import uuid
from urllib.parse import urlparse, quote as urlquote

from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import authenticated
from tornado.web import RequestHandler

from jupyterhub.services.auth import HubAuthenticated

from .launcher import Launcher


HubAuthenticated.hub_auth


class CreateSharedLink(HubAuthenticated, RequestHandler):
    ...


class OpenSharedLink(HubAuthenticated, RequestHandler):
    @authenticated
    async def get(self, source_username, source_server_name, image, source_path):
        dest_path = self.get_argument('dest_path', source_path)
        launcher = Launcher(self.get_current_user(), self.hub_auth.api_token)

        # Ensure destination has a server to share into.
        dest_server_name = f'shared-link-{str(uuid.uuid4())[:8]}'
        # TODO Use existing server with this image if it exists.
        result = await launcher.launch(image, dest_server_name)

        if result['status'] == 'pending':
            here = (f"{os.getenv('JUPYTERHUB_SERVICE_URL')}/{source_username}/"
                    f"{source_server_name}/{image}/{source_path}")
            redirect_url = f"{result['url']}?next={urlquote(here)}"
            # Redirect to progress bar, and then back here to try again.
            self.redirect(redirect_url)
        assert result['status'] == 'running'

        resp = await launcher.api_request(
            f'users/{source_username}',
            method='GET',
        )
        source_user_data = json.loads(resp.body.decode('utf-8'))
        print('USER DATA', source_user_data)

        source_server_url = source_user_data['servers'][source_server_name]['url']
        base_url = os.getenv('JUPYTERHUB_API_URL', '')[:-7]
        # HACK to avoid confusing /hub/ -> / -> /hub -> ... redirect loop
        base_url = "http://127.0.0.1:8000"
        content_url = f'{base_url}/{source_server_url}api/contents/{source_path}'
        headers = {'Authorization': f'token {launcher.hub_api_token}'}
        req = HTTPRequest(content_url, headers=headers)
        resp = await AsyncHTTPClient().fetch(req)
        content = resp.body

        # Copy content into destination server.
        to_username = launcher.user['name']
        dest_url = (f'{base_url}/user/{to_username}/{dest_server_name}/'
                    f'api/contents/{dest_path}')
        req = HTTPRequest(dest_url, "PUT", headers=headers, body=content)
        resp = await AsyncHTTPClient().fetch(req)

        redirect_url = f"{result['url']}/tree/{dest_path}"

        # necessary?
        redirect_url = redirect_url if redirect_url.startswith('/') else '/' + redirect_url

        self.redirect(redirect_url)


def main():
    app = Application(
        [
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + r'([^/]*)/([^/]*)/([^/]*)/(.*)/?', OpenSharedLink)
        ]
    )

    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    http_server.listen(url.port, url.hostname)

    IOLoop.current().start()


main()
