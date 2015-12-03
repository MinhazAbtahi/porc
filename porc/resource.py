from . import util
import json
from .response import Response
import copy
from google.appengine.api import urlfetch

try:
    # python 2
    from urllib import quote
    from urllib import urlencode
except ImportError:
    # python 3
    from urllib.parse import quote
    from urllib.parse import urlencode


class Resource(object):

    def __init__(self, uri, use_async=False, **kwargs):
        self.uri = uri
        self.opts = kwargs
        self.session = urlfetch
        self.use_async = use_async
        kwargs['hooks'] = {
            "response": self._handle_response
        }
        for obj in [self.session]:
            for key, value in kwargs.items():
                setattr(obj, key, value)

    def _merge_paths(self, path):
        if path:
            if isinstance(path, list):
                path = '/'.join([quote(str(elem), '') for elem in path])
            return '/'.join([self.uri, path])
        else:
            return self.uri

    def _make_request(self, method, path='', body=None, headers={}):
        """
        Executes the request based on the given body and headers
        along with options set on the object.
        """
        uri = self._merge_paths(path)
        opts = dict(headers=headers)
        opts['headers'].update(self.session.headers)
        session = self.session
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
                uri += '?' + urlencode(body, doseq=True)
            elif method.lower() == 'post':
                opts['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
                opts['payload'] = urlencode(body, doseq=True)
            else:
                opts['payload'] = json.dumps(body)

        return session.fetch(uri, method=getattr(urlfetch, method), **opts)

    def _handle_response(self, response, *args, **kwargs):
        return Response(response)
