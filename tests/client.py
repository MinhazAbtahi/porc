from datetime import datetime
import time
import vcr
import porc
import unittest
from .credentials import API_KEY

import requests
requests.packages.urllib3.disable_warnings()

class ClientTest(unittest.TestCase):

    def setUp(self):
        self.api_key = API_KEY
        if API_KEY == None:
            print "No API key provided!"
            sys.exit(-1)

        self.client = porc.Client(self.api_key)
        self.collections = ['COLLECTION_1', 'COLLECTION_2']
        self.keys = ['KEY_1', 'KEY_2']
        self.client.ping().raise_for_status()

    # N.B.: TESTS MUST CLEAN UP AFTER THEMSELVES

    @vcr.use_cassette('fixtures/client/ping.yaml', filter_headers=['Authorization'])
    def test_ping(self):
        self.client.ping().raise_for_status()

    @vcr.use_cassette('fixtures/client/head.yaml', filter_headers=['Authorization'])
    def test_head(self):
        resp = self.client.put(
            self.collections[0], self.keys[0], {"derp": True})
        ref = resp.ref
        resp.raise_for_status()

        # Test top level API
        resp = self.client.head()
        resp.raise_for_status()
        assert resp.status_code is 200
        # Test collection
        resp = self.client.head(self.collections[0])
        resp.raise_for_status()
        assert resp.status_code is 200
        # Test key
        resp = self.client.head(self.collections[0], self.keys[0])
        resp.raise_for_status()
        assert resp.status_code is 200
        assert resp.ref == ref
        # Test ref
        resp = self.client.head(self.collections[0], self.keys[0], ref)
        resp.raise_for_status()
        assert resp.status_code is 200
        assert resp.ref == ref

    @vcr.use_cassette('fixtures/client/get.yaml', filter_headers=['Authorization'])
    def test_get(self):
        # test_delete deletes a collection, wait 5s when the VCR is recording.
        # time.sleep(5)
        # test 404
        resp = self.client.get(self.collections[0], self.keys[0])
        assert resp.status_code == 404
        # create item
        resp = self.client.put(
            self.collections[0], self.keys[0], {"derp": True})
        ref = resp.ref
        resp.raise_for_status()
        # test 200 with ref
        resp = self.client.get(self.collections[0], self.keys[0], ref)
        resp.raise_for_status()
        # test 200
        resp = self.client.get(self.collections[0], self.keys[0])
        resp.raise_for_status()
        # cleanup
        self.client.delete(
            self.collections[0], self.keys[0]).raise_for_status()

    @vcr.use_cassette('fixtures/client/post.yaml', filter_headers=['Authorization'])
    def test_post(self):
                # test creates
        resp = self.client.post(self.collections[0], {"derp": True})
        key = resp.key
        ref = resp.ref
        resp.raise_for_status()
        # test get with generated ref
        self.client.get(self.collections[0], key, ref).raise_for_status()
        # cleanup
        self.client.delete(self.collections[0], key, ref).raise_for_status()
        self.client.delete(self.collections[0], key).raise_for_status()

    @vcr.use_cassette('fixtures/client/put.yaml', filter_headers=['Authorization'])
    def test_put(self):
        # make sure the self.key[0] does not exist for this test
        self.client.delete(self.collections[0], self.keys[0]).raise_for_status()
        # test creates with If-None-Match
        resp = self.client.put(
            self.collections[0], self.keys[0], {
              "derp": True,
              "herp": False
            }, False)
        resp.raise_for_status()
        # get item
        resp = self.client.get(resp.collection, resp.key)
        resp.raise_for_status()
        # modify the item
        assert 'derp' in [key for key in resp]
        resp['derp'] = False
        del resp['herp']
        # test update with If-Match
        self.client.put(
            resp.collection, resp.key, resp.json, resp.ref).raise_for_status()
        # test update with neither
        resp['derp'] = True
        self.client.put(
            resp.collection, resp.key, resp.json).raise_for_status()
        # delete
        self.client.delete(
            self.collections[0], self.keys[0]).raise_for_status()

    @vcr.use_cassette('fixtures/client/put_url_escape.yaml', filter_headers=['Authorization'])
    def test_put_url_escape(self):
        key = "007: Tomorrow Never Dies / 007: The World is Not Enough"
        self.client.put('movies', key, {}).raise_for_status()
        self.client.get('movies', key).raise_for_status()
        self.client.delete('movies', key).raise_for_status()

    @vcr.use_cassette('fixtures/client/patch.yaml', filter_headers=['Authorization'])
    def test_patch(self):
        # create initial object
        resp = self.client.put(self.collections[0], self.keys[0], {
            "derp": False,
            "herp": True,
            "foo": False,
            "baz": True,
            "eggs": False,
            "count": 1
        })
        resp.raise_for_status()

        # test default patch
        self.client.patch(self.collections[0], self.keys[0], [
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
        resp = self.client.patch(self.collections[0], self.keys[0], patch, ref)
        resp = self.client.get(resp.collection, resp.key)
        resp.raise_for_status()
        assert resp['herp'] == False
        assert 'derp' not in [key for key in resp]
        assert resp['bar'] == True
        assert resp['spam'] == True
        assert resp['herpderp'] == False
        assert resp['count'] == 1

    @vcr.use_cassette('fixtures/client/patch_merge.yaml', filter_headers=['Authorization'])
    def test_patch_merge(self):
        # create initial object
        resp = self.client.put(self.collections[0], self.keys[0], {
        "derp": True,
        "herp": False
        })
        resp.raise_for_status()

        # test patch_merge without ref
        resp = self.client.patch_merge(self.collections[0], self.keys[0], {
            "foo": True,
        })
        resp.raise_for_status()
        resp = self.client.get(resp.collection, resp.key)
        assert resp['herp'] == False
        assert resp['derp'] == True
        assert resp['foo'] == True

        # test patch merge with ref
        ref = resp.ref
        resp = self.client.patch_merge(self.collections[0], self.keys[0], {
            "bar": False
        }, ref)
        resp.raise_for_status()
        resp = self.client.get(resp.collection, resp.key)
        resp.raise_for_status()
        assert resp['herp'] == False
        assert resp['derp'] == True
        assert resp['foo'] == True
        assert resp['bar'] == False

    @vcr.use_cassette('fixtures/client/delete.yaml', filter_headers=['Authorization'])
    def test_delete(self):
                # create
        resp = self.client.post(self.collections[0], {"derp": True})
        resp.raise_for_status()
        # delete a ref
        self.client.delete(
            resp.collection, resp.key, resp.ref).raise_for_status()
        # delete purge
        self.client.delete(resp.collection, resp.key).raise_for_status()
        # delete collection
        self.client.delete(resp.collection).raise_for_status()

    @vcr.use_cassette('fixtures/client/refs.yaml', filter_headers=['Authorization'])
    def test_refs(self):
        # create
        resp = self.client.post(self.collections[0], {"derp": True})
        resp.raise_for_status()
        # list
        ref_resp = self.client.refs(resp.collection, resp.key, values=False)
        ref_resp.raise_for_status()
        assert ref_resp['count'] == 1
        # delete
        self.client.delete(resp.collection, resp.key).raise_for_status()

    @vcr.use_cassette('fixtures/client/list.yaml', filter_headers=['Authorization'])
    def test_list(self):
        # create
        resp = self.client.post(self.collections[0], {"derp": True})
        resp.raise_for_status()
        # list
        pages = self.client.list(resp.collection, limit=1)
        page = pages.next()
        page.raise_for_status()
        assert page['count'] == 1
        # delete
        self.client.delete(resp.collection, resp.key).raise_for_status()

    @vcr.use_cassette('fixtures/client/search.yaml', filter_headers=['Authorization'])
    def test_search(self):
        # create
        resp = self.client.post(self.collections[0], {"herp": "hello"})
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
        resp = self.client.post(self.collections[0], {"herp": 2})
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


    @vcr.use_cassette('fixtures/client/search_events.yaml', filter_headers=['Authorization'])
    def test_search_events(self):
        # Create some normal data
        resp = self.client.post(self.collections[0], {"name": "shark"})
        resp.raise_for_status()
        resp = self.client.post(self.collections[0], {"name": "dog"})
        resp.raise_for_status()
        resp = self.client.post(self.collections[0], {"name": "bat"})
        resp.raise_for_status()

        # Create some events
        resp = self.client.post_event(self.collections[0], self.keys[0], 'slog', {"name": "dog"})
        resp.raise_for_status()
        resp = self.client.post_event(self.collections[0], self.keys[0], 'slog', {"name": "cat"})
        resp.raise_for_status()
        resp = self.client.post_event(self.collections[0], self.keys[0], 'slog', {"name": "giraffe"})
        resp.raise_for_status()

        # Wait for everything to get indexed in search
        time.sleep(3)

        # Do an event search for dogs (should yield 1 event)
        s1 = porc.Search().query('dog').limit(5).kind("event")
        pages = self.client.search(self.collections[0], s1).all()
        assert len(pages) == 1
        assert pages[0]["path"]["kind"] == "event"
        assert pages[0]["value"]["name"] == "dog"

        # Do a item/event search for dog (should yield 2)
        s2 = porc.Search().query('dog').limit(5).kind("event item")
        pages = self.client.search(self.collections[0], s2).all()
        assert len(pages) == 2

        # Do a normal search for dog (should yield 1 item)
        s3 = porc.Search().query('dog').limit(5)
        pages = self.client.search(self.collections[0], s3).all()
        assert len(pages) == 1
        assert pages[0]["path"]["kind"] == "item"
        assert pages[0]["value"]["name"] == "dog"

        # Delete the collection
        self.client.delete(self.collections[0]).raise_for_status()


    @vcr.use_cassette('fixtures/client/relations.yaml', filter_headers=['Authorization'])
    def test_crud_relations(self):
        # create two items
        responses = []
        for item in [{"herp": "hello"}, {"burp": "goodbye"}]:
            resp = self.client.post(self.collections[0], item)
            resp.raise_for_status()
            responses.append(resp)
        # get relation, 404 or 200 and count = 0
        resp = self.client.get_relations(
            self.collections[0], responses[0].key, 'friends')
        if resp.status_code == 200:
            assert resp['count'] == 0
        else:
            assert resp.status_code == 404
        # make relation, 201
        resp = self.client.put_relation(
            self.collections[0],
            responses[0].key,
            'friends',
            self.collections[0],
            responses[1].key
        )
        resp.raise_for_status()
        # get relation, 200
        resp = self.client.get_relations(
            self.collections[0], responses[0].key, 'friends')
        resp.raise_for_status()
        assert resp['count'] == 1
        # delete relation
        self.client.delete_relation(
            self.collections[0],
            responses[0].key,
            'friends',
            self.collections[0],
            responses[1].key
        )
        # delete collection
        self.client.delete(self.collections[0]).raise_for_status()

    @vcr.use_cassette('fixtures/client/events.yaml', filter_headers=['Authorization'])
    def test_crud_events(self):
        # create an event
        resp = self.client.post_event(
            self.collections[0], self.keys[0], 'log', {'herp': 'derp'})
        resp.raise_for_status()
        # create an event with a timestamp
        timestamp = resp.headers['Location'].split('/')[6]
        resp = self.client.post_event(
            self.collections[0], self.keys[0], 'log', {'herp': 'derp'}, timestamp)
        resp.raise_for_status()
        # get an event
        resp = self.client.get_event(
            resp.collection, resp.key, resp.type, timestamp, resp.ordinal)
        resp.raise_for_status()
        # update an event
        resp = self.client.put_event(
            resp.collection, resp.key, resp.type, timestamp, resp.ordinal, {'herp': 'lol'})
        resp.raise_for_status()
        # update with ref
        resp = self.client.put_event(
            resp.collection, resp.key, resp.type, resp.timestamp, resp.ordinal, {'herp': 'rofl'}, resp.ref)
        resp.raise_for_status()
        # list all events
        pages = self.client.list_events(
            resp.collection, resp.key, resp.type, limit=1, afterEvent=datetime.utcfromtimestamp(0))
        page = pages.next()
        page.raise_for_status()
        assert page['count'] == 1
        # delete event with ref
        self.client.delete_event(
            resp.collection, resp.key, resp.type, timestamp, resp.ordinal, resp.ref).raise_for_status()
        # create an event
        resp = self.client.post_event(
            self.collections[0], self.keys[0], 'log', {'herp': 'derp'})
        resp.raise_for_status()
        # delete event without ref
        timestamp = resp.headers['Location'].split('/')[6]
        self.client.delete_event(
            resp.collection, resp.key, resp.type, timestamp, resp.ordinal).raise_for_status()

    @vcr.use_cassette('fixtures/client/async.yaml', filter_headers=['Authorization'])
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
