import json
import requests
from .response import Response
from requests_futures.sessions import FuturesSession

try:
    # python 2
    from urllib import quote
    from urlparse import urljoin
except ImportError:
    # python 3
    from urllib.parse import quote, urljoin


class Resource(object):
    def __init__(self, uri, use_async=False, **kwargs):
        self.uri = uri
        self.opts = kwargs
        self.session = requests.Session()
        self.async_session = FuturesSession()
        self.use_async = use_async
        kwargs['hooks'] = {
            "response": self._handle_response
        }
        for obj in [self.session, self.async_session]:
            for key, value in kwargs.items():
                setattr(obj, key, value)

    def _make_path(self, path):
        # If the first element of the list isn't v0, insert it
        if len(path) > 0 and path[0] != "v0":
            path.insert(0, "v0")
        elif len(path) == 0:
            path = ["v0"]

        # Escape the components of the path
        return '/'.join([quote(str(elem), '') for elem in path])

    def _request(self, method, path = [], body = None, headers = {}):
        """
        Executes the request based on the given body and headers
        along with options set on the object.
        """
        if isinstance(path, list):
            path = self._make_path(path)

        uri = urljoin(self.uri, path)

        opts = dict(headers=headers)
        session = self.async_session if self.use_async else self.session
        # normalize body according to method and type
        if body != None:
            if method.lower() in ['head', 'get', 'delete']:
                if type(body) == dict:
                    # convert True and False to true and false
                    for key, value in list(body.items()):
                        if value is True:
                            body[key] = 'true'
                        elif value is False:
                            body[key] = 'false'
                opts['params'] = body
            else:
                opts['data'] = json.dumps(body)

        return session.request(method, uri, **opts)

    def _handle_response(self, response, *args, **kwargs):
        return Response(response)
