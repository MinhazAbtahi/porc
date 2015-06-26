import time
import unittest
import porc

from . import API_KEY, API_URL

class PagesTest(unittest.TestCase):
    def setUp(self):
        self.client = porc.Client(API_KEY, API_URL)
        self.collection = self.id().split(".", 2)[2]
        self.pages = self.client.search(self.collection, '*', limit=1)

        # If the collection does not contain a sentinel value, insert
        # some data
        resp = self.client.get(self.collection, self.collection)
        if resp.status_code == 404:
            self.client.put(self.collection, self.collection, {'lol': True})\
                       .raise_for_status()
            self.client.post(self.collection, {'lol': True}).raise_for_status()
            self.client.post(self.collection, {'lol': True}).raise_for_status()

            # Give the server a chance to index everything
            time.sleep(3)

    def test_reset(self):
        resp = self.pages.next()
        resp.raise_for_status()
        assert resp.links.get('prev', None) == None
        self.pages.reset()
        resp = self.pages.next()
        resp.raise_for_status()
        assert resp.links.get('prev', None) == None

    def test_next(self):
        resp = self.pages.next()
        resp.raise_for_status()

    def test_prev(self):
        resp = self.pages.next()
        resp.raise_for_status()
        resp = self.pages.next()
        resp.raise_for_status()
        resp = self.pages.prev()
        resp.raise_for_status()

    def test_all(self):
        all_items = self.pages.all()
        assert len(all_items) > 0

    def test_iter(self):
        pages = [page for page in self.pages]
        [page.raise_for_status() for page in pages]
