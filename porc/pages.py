from .resource import Resource
from collections import Iterator

class Pages(Iterator):
    def __init__(self, opts, url, path, params):
        self.initialPath = path
        self.nextPath = path
        self.prevPath = None
        self.resource = Resource(url, **opts)
        self.params = params

    def _move(self, path, querydict = {}, **headers):
        if path is None:
            raise StopIteration

        # Make a copy of parameters
        params = self.params.copy()
        params.update(querydict)

        # Get the page
        response = self.resource._request('GET', path, params, **headers)

        # Extract the next/prev links
        self.nextPath = response.links.get('next', {}).get('url')
        self.prevPath = response.links.get('prev', {}).get('url')
        return response

    def reset(self):
        """
        Clear the page's current place.

            page_1 = page.next().result()
            page_2 = page.next().result()
            page.reset()
            page_x = page.next().result()
            assert page_x.url == page_1.url
        """
        self.nextPath = self.initialPath
        self.prevPath = None

    def next(self, querydict={}, **headers):
        """
        Gets the next page of results.
        Raises `StopIteration` when there are no more results.
        """
        return self._move(self.nextPath, querydict, **headers)

    def __next__(self):
        return self.next()

    def prev(self, querydict={}, **headers):
        """
        Gets the previous page of results.
        Raises `StopIteration` when there are no more results.

        Note: Only collection searches provide a `prev` value.
        For all others, `prev` will always return `StopIteration`.
        """
        return self._move(self.prevPath, querydict, **headers)

    def all(self):
        results = []
        for response in self:
            response.raise_for_status()
            results.extend(response['results'])
        return results
