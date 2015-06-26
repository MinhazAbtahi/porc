from datetime import datetime
import time
import vcr
import porc
import unittest
from . import API_KEY, API_URL

class ClientTest(unittest.TestCase):

    def setUp(self):
        self.collection = self.id().split(".", 2)[2]
        self.client = porc.Client(API_KEY, API_URL)
        self.keys = ['KEY_1', 'KEY_2']

        # Make sure any old versions are gone
        resp = self.client.delete(self.collection)
        if resp.status_code > 300 and resp.status_code != 404:
            self.fail("Unexpected status while cleaning up: %d" % (resp.status_code))

    def test_ping(self):
        self.client.ping().raise_for_status()

    def test_head(self):
        resp = self.client.put(self.collection, self.keys[0], {"derp": True})
        ref = resp.ref
        resp.raise_for_status()

        # Test top level API
        resp = self.client.head()
        resp.raise_for_status()
        assert resp.status_code is 200
        # Test collection
        resp = self.client.head(self.collection)
        resp.raise_for_status()
        assert resp.status_code is 200
        # Test key
        resp = self.client.head(self.collection, self.keys[0])
        resp.raise_for_status()
        assert resp.status_code is 200
        assert resp.ref == ref
        # Test ref
        resp = self.client.head(self.collection, self.keys[0], ref)
        resp.raise_for_status()
        assert resp.status_code is 200
        assert resp.ref == ref

    def test_get(self):
        # test 404
        resp = self.client.get(self.collection, self.keys[0])
        assert resp.status_code == 404
        # create item
        resp = self.client.put(self.collection, self.keys[0], {"derp": True})
        ref = resp.ref
        resp.raise_for_status()
        # test 200 with ref
        resp = self.client.get(self.collection, self.keys[0], ref)
        resp.raise_for_status()
        # test 200
        resp = self.client.get(self.collection, self.keys[0])
        resp.raise_for_status()

    def test_post(self):
        # test creates
        resp = self.client.post(self.collection, {"derp": True})
        key = resp.key
        ref = resp.ref
        resp.raise_for_status()
        # test get with generated ref
        self.client.get(self.collection, key, ref).raise_for_status()

    def test_put(self):
        # test creates with If-None-Match
        resp = self.client.put(
            self.collection, self.keys[0], {
              "derp": True,
              "herp": False
            }, False)
        resp.raise_for_status()
        # get item
        resp = self.client.get(self.collection, resp.key)
        resp.raise_for_status()
        # modify the item
        assert 'derp' in [key for key in resp]
        resp['derp'] = False
        del resp['herp']
        # test update with If-Match
        self.client.put(self.collection, resp.key, resp.json, resp.ref).raise_for_status()
        # test update with neither
        resp['derp'] = True
        self.client.put(self.collection, resp.key, resp.json).raise_for_status()

    def test_put_url_escape(self):
        key = "007: Tomorrow Never Dies / 007: The World is Not Enough"
        self.client.put(self.collection, key, {}).raise_for_status()
        self.client.get(self.collection, key).raise_for_status()

    def test_patch(self):
        # create initial object
        resp = self.client.put(self.collection, self.keys[0], {
            "derp": False,
            "herp": True,
            "foo": False,
            "baz": True,
            "eggs": False,
            "count": 1
        })
        resp.raise_for_status()

        # test default patch
        self.client.patch(self.collection, self.keys[0], [
            {"op": "add",
            "path": "derp",
            "value": True}
        ])
        resp = self.client.get(resp.collection, resp.key)
        resp.raise_for_status()
        assert resp['herp'] == True
        assert resp['derp'] == True
        assert resp['foo'] == False

        # test patch with specific ref and with Patch
        ref = resp.ref
        patch = porc.Patch()
        patch.add("bar", True).remove("derp").replace("herp", False).move("baz", "spam").copy("eggs", "herpderp").test("foo", False).increment("count").increment("count", 2).decrement("count").decrement("count",2)
        resp = self.client.patch(self.collection, self.keys[0], patch, ref)
        resp = self.client.get(resp.collection, resp.key)
        resp.raise_for_status()
        assert resp['herp'] == False
        assert 'derp' not in [key for key in resp]
        assert resp['bar'] == True
        assert resp['spam'] == True
        assert resp['herpderp'] == False
        assert resp['count'] == 1

    def test_patch_merge(self):
        # create initial object
        resp = self.client.put(self.collection, self.keys[0], {
        "derp": True,
        "herp": False
        })
        resp.raise_for_status()

        # test patch_merge without ref
        resp = self.client.patch_merge(self.collection, self.keys[0], {
            "foo": True,
        })
        resp.raise_for_status()
        resp = self.client.get(resp.collection, resp.key)
        assert resp['herp'] == False
        assert resp['derp'] == True
        assert resp['foo'] == True

        # test patch merge with ref
        ref = resp.ref
        resp = self.client.patch_merge(self.collection, self.keys[0], {
            "bar": False
        }, ref)
        resp.raise_for_status()
        resp = self.client.get(resp.collection, resp.key)
        resp.raise_for_status()
        assert resp['herp'] == False
        assert resp['derp'] == True
        assert resp['foo'] == True
        assert resp['bar'] == False

    def test_delete(self):
                # create
        resp = self.client.post(self.collection, {"derp": True})
        resp.raise_for_status()
        # delete a ref
        self.client.delete(
            resp.collection, resp.key, resp.ref).raise_for_status()
        # delete purge
        self.client.delete(resp.collection, resp.key).raise_for_status()
        # delete collection
        self.client.delete(resp.collection).raise_for_status()

    def test_refs(self):
        # create
        resp = self.client.post(self.collection, {"derp": True})
        resp.raise_for_status()
        # list
        ref_resp = self.client.refs(resp.collection, resp.key, values=False)
        ref_resp.raise_for_status()
        assert ref_resp['count'] == 1
        # delete
        self.client.delete(resp.collection, resp.key).raise_for_status()

    def test_list(self):
        # create
        resp = self.client.post(self.collection, {"derp": True})
        resp.raise_for_status()
        # list
        pages = self.client.list(resp.collection, limit=1)
        page = pages.next()
        page.raise_for_status()
        assert page['count'] == 1
        # delete
        self.client.delete(resp.collection, resp.key).raise_for_status()

    def test_search(self):
        # create
        resp = self.client.post(self.collection, {"herp": "hello"})
        resp.raise_for_status()
        # wait; search is eventually consistent
        time.sleep(3)
        # list
        pages = self.client.search(resp.collection, 'herp:hello', limit=1)
        page = pages.next()
        page.raise_for_status()
        assert page['count'] == 1
        # delete
        self.client.delete(resp.collection, resp.key).raise_for_status()

        # Test Search with a Search Object
        # create
        resp = self.client.post(self.collection, {"herp": 2})
        resp.raise_for_status()
        # wait; search is eventually consistent
        time.sleep(3)
        # build a search query
        search = porc.Search()
        search = search.query("*").limit(1).sort("herp", "desc").aggregate("stats", "herp")
        # list
        pages = self.client.search(resp.collection, search)
        page = pages.next()
        page.raise_for_status()
        assert page['count'] == 1
        # delete
        self.client.delete(resp.collection, resp.key).raise_for_status()

    def test_crud_relations(self):
        # create two items
        responses = []
        for item in [{"herp": "hello"}, {"burp": "goodbye"}]:
            resp = self.client.post(self.collection, item)
            resp.raise_for_status()
            responses.append(resp)
        # get relation, 404 or 200 and count = 0
        resp = self.client.get_relations(
            self.collection, responses[0].key, 'friends')
        if resp.status_code == 200:
            assert resp['count'] == 0
        else:
            assert resp.status_code == 404
        # make relation, 201
        resp = self.client.put_relation(
            self.collection,
            responses[0].key,
            'friends',
            self.collection,
            responses[1].key
        )
        resp.raise_for_status()
        # get relation, 200
        resp = self.client.get_relations(
            self.collection, responses[0].key, 'friends')
        resp.raise_for_status()
        assert resp['count'] == 1
        # delete relation
        self.client.delete_relation(
            self.collection,
            responses[0].key,
            'friends',
            self.collection,
            responses[1].key
        )
        # delete collection
        self.client.delete(self.collection).raise_for_status()

    def test_crud_events(self):
        # create an event
        resp = self.client.post_event(
            self.collection, self.keys[0], 'log', {'herp': 'derp'})
        resp.raise_for_status()
        # create an event with a timestamp
        timestamp = resp.headers['Location'].split('/')[6]
        resp = self.client.post_event(
            self.collection, self.keys[0], 'log', {'herp': 'derp'}, timestamp)
        resp.raise_for_status()
        # get an event
        resp = self.client.get_event(
            self.collection, resp.key, resp.type, timestamp, resp.ordinal)
        resp.raise_for_status()
        # update an event
        resp = self.client.put_event(
            self.collection, resp.key, resp.type, timestamp, resp.ordinal, {'herp': 'lol'})
        resp.raise_for_status()
        # update with ref
        resp = self.client.put_event(
            self.collection, resp.key, resp.type, resp.timestamp, resp.ordinal, {'herp': 'rofl'}, resp.ref)
        resp.raise_for_status()
        # list all events
        pages = self.client.list_events(
            self.collection, resp.key, resp.type, limit=1, afterEvent=datetime.utcfromtimestamp(0))
        page = pages.next()
        page.raise_for_status()
        assert page['count'] == 1
        # delete event with ref
        self.client.delete_event(
            self.collection, resp.key, resp.type, timestamp, resp.ordinal, resp.ref).raise_for_status()
        # create an event
        resp = self.client.post_event(
            self.collection, self.keys[0], 'log', {'herp': 'derp'})
        resp.raise_for_status()
        # delete event without ref
        timestamp = resp.headers['Location'].split('/')[6]
        self.client.delete_event(
            self.collection, resp.key, resp.type, timestamp, resp.ordinal).raise_for_status()

    def test_async(self):
        # add three items
        with self.client.async() as c:
            futures = [
                c.post(self.collections[1], {"holy gosh": True}),
                c.post(self.collections[1], {"holy gosh": True}),
                c.post(self.collections[1], {"holy gosh": True})
            ]
            responses = [future.result() for future in futures]
            [response.raise_for_status() for response in responses]
        # ensure they all exist
        with self.client.async() as c:
            futures = [
                c.get(self.collections[1], responses[0].key),
                c.get(self.collections[1], responses[1].key),
                c.get(self.collections[1], responses[2].key)
            ]
            responses = [future.result() for future in futures]
            [response.raise_for_status() for response in responses]
        # delete all three
        with self.client.async() as c:
            futures = [
                c.delete(self.collections[1], responses[0].key),
                c.delete(self.collections[1], responses[1].key),
                c.delete(self.collections[1], responses[2].key)
            ]
            responses = [future.result() for future in futures]
            [response.raise_for_status() for response in responses]
