# Porc

[![Build Status](https://travis-ci.org/orchestrate-io/porc.svg?branch=master)](https://travis-ci.org/orchestrate-io/porc)
[![Coverage Status](https://coveralls.io/repos/orchestrate-io/porc/badge.png?branch=master)](https://coveralls.io/r/orchestrate-io/porc?branch=master)
[![PyPI version](https://badge.fury.io/py/porc.svg)](http://badge.fury.io/py/porc)
[![PyPi downloads](https://pypip.in/d/porc/badge.png)](https://crate.io/packages/porc/)

An effortless, asynchronous Python client for [orchestrate.io][].

## Install

    pip install porc

Don't have [pip][]? [Get it!](http://pip.readthedocs.org/en/latest/installing.html) It's neat :D


## Usage

Let's dive right in:

```python
from porc import Client

# create a client using the default AWS US East host: https://api.orchestrate.io
client = Client(YOUR_API_KEY)

# create a client using the EU datacenter
host = "https://api.aws-eu-west-1.orchestrate.io/"
client = Client(YOUR_API_KEY, host)

# make sure our API key works
client.ping().raise_for_status()

# get and update an item
item = client.get(COLLECTION, KEY)
item['was_modified'] = True
client.put(item.collection, item.key, item.json, item.ref).raise_for_status()

# asynchronously get two items
with client.async() as c:
    futures = [
        c.get(COLLECTION, KEY_1),
        c.get(COLLECTION, KEY_2)
    ]
    responses = [future.result() for future in futures]
    [response.raise_for_status() for response in responses]

# iterate through search results
pages = client.search(COLLECTION, QUERY)
for page in pages:
    # prints 200
    print page.status_code
    # prints number of items returned by page
    print page['count']

# get every item in a collection
items = client.list(COLLECTION).all()
# prints number of items in collection
print len(items)
```

## Table of Contents

* [Client(api_key, custom_url=None, **options)](#client)
* [Client.get(collection, key, ref=None)](#clientget)
* [Client.head(collection=None, key=None, ref=None)](#clienthead)
* [Client.post(collection, item)](#clientpost)
* [Client.put(collection, key, item, ref=None)](#clientput)
* [Client.patch(collection, key, item, ref=None)](#clientpatch)
* [Client.patch_merge(collection, key, item, ref=None)](#clientpatch_merge)
* [Client.delete(collection, key=None, ref=None)](#clientdelete)
* [Client.refs(collection, key, **params)](#clientrefs)
* [Client.list(collection, **params)](#clientlist)
* [Client.search(collection, query, **params)](#clientsearch)
* [Client.get_relations(collection, key, *relations)](#clientget_relations)
* [Client.put_relation(collection, key, relation, to_collection, to_key)](#clientput_relation)
* [Client.delete_relation(collection, key, relation, to_collection, to_key)](#clientdelete_relation)
* [Client.get_event(collection, key, event_type, timestamp, ordinal)](#clientget_event)
* [Client.post_event(collection, key, event_type, data, timestamp=None)](#clientpost_event)
* [Client.put_event(collection, key, event_type, timestamp, ordinal, data, ref=None)](#clientput_event)
* [Client.delete_event(collection, key, event_type, timestamp, ordinal, ref=None)](#clientdelete_event)
* [Client.list_events(collection, key, event_type, **params)](#clientlist_events)
* [Client.async()](#clientasync)
* [Pages](#page)
* [Pages.next(querydict={}, **headers)](#pagesnext)
* [Pages.prev(querydict={}, **headers)](#pagesprev)
* [Pages.reset()](#pagesreset)
* [Pages.all()](#pagesall)
* [Patch](#patch)
* [Patch.add(path, value)](#patchadd)
* [Patch.remove(path)](#patchremove)
* [Patch.replace(path, value)](#patchreplace)
* [Patch.move(old_path, new_path)](#patchmove)
* [Patch.copy(original, copy)](#patchcopy)
* [Patch.test(path, value)](#patchtest)
* [Patch.increment(path, value=1)](#patchincrement)
* [Patch.decrement(path, value=1)](#patchdecrement)
* [Search](#search)
* [Search.query](#searchquery)
* [Search.limit](#searchlimit)
* [Search.offset](#searchoffset)
* [Search.aggregate](#searchaggregate)
* [Search.sort](#searchsort)
* [Response](#response)

## API Reference

### Client

```python
from porc import Client

client = Client(API_KEY)
```

The thing you'll use to make requests. It's the only object you'll need to invoke directly.

By default, the client makes requests to <https://api.orchestrate.io/v0>. If you need to make requests against a different URL, you can pass it as an argument to the constructor:

```python
client = Client(API_KEY, "https://your_domain.com")
```

By default, the client makes synchronous requests. To make asynchronous requests, see [Client.async](#clientasync).

### Client.get

```python
item = client.get('a_collection', 'a_key')
# make sure the request succeeded
item.raise_for_status()
# prints your item's ref value
print item.ref
# prints your item's fields and values as a dict
print item.json
# prints a given field from the item's json
print item[FIELD]
```

Returns the item associated with a given key from a given collection.
The optional `ref` argument can retrieve a specific version of an item, like so:

```python
item = client.get('a_collection', 'a_key', 'a_ref')
```

This method returns a [Response](#response) object.

### Client.head
This method is useful to get the `ref` of an item or to test the existence of an item, but does not return the body of the document in order to lower the overall size of the HTTP payload.

```python
ref = client.head('a_collection', 'a_key').ref
```

### Client.post

```python
response = client.post('a_collection', {
  "derp": True
})
# make sure the request succeeded
response.raise_for_status()
# prints the item's generated key
print response.key
# prints the item version's ref
print response.ref
```

Inserts an item into a collection, allowing the server to generate a key for it.

This method returns a [Response](#response) object.

### Client.put

```python
response = client.put('a_collection', 'a_key', {
  "derp": True
})
# make sure the request succeeded
response.raise_for_status()
# prints the item's key
print response.key
# prints the item version's ref
print response.ref
```

Inserts an item into a collection at a given key, or updates the value previously at that key.

The optional `ref` argument can be used to perform conditional updates.
To update only if your `ref` matches the latest version's, provide it to the method:

```python
response = client.put('a_collection', 'a_key', {
  "derp": True
}, 'a_ref')
```

To insert only if there is no item associated with a key, provide `False` instead:

```python
response = client.put('a_collection', 'a_key', {
  "derp": True
}, False)
```

This method returns a [Response](#response) object.

### Client.patch
Defines a set of operations which mutate a Key/Value item sequentially based on array order. Each operation must be specified by an operation type, a path or set of paths, and a value. To learn more about the types of operations, please see http://orchestrate.io/docs/apiref#keyvalue-patch.

```python
from porc import Patch

patch = Patch()
patch.add("derp", True).remove("herp")

client.patch('a_collection', 'a_key', patch)
```

The `porc.Patch` module provides an easy way to build an operation set document. You can read more about [`porc.Patch` below](#Patch).

It is also possible to build the operation set yourself.

```python

op_set = [
  {'op': 'add',
  'path': 'derp',
  'value': True},
  {'op': 'remove',
  'path': 'herp'}
  ]

client.patch('a_collection', 'a_key', op_set)
```

The optional `ref` argument can be used to perform conditional updates.
To update only if your `ref` matches the latest version's, provide it to the method:

```python
from porc import Patch

patch = Patch()
patch.add("derp", True).remove("herp").decrement("foo")

response = client.get('a_collection', 'a_key')

res = client.patch('a_collection', 'a_key', patch, response.ref)
# Only applies operations if response.ref is the current reference
# make sure the request succeeded
res.raise_for_status()
```

To learn more about `refs`, see http://orchestrate.io/docs/apiref#refs

The `If-None-Match` header is not relevant to a `PATCH` request, since the key MUST already exist for the patch operation to succeed.

This method returns a [Response](#response) object.

### Client.patch_merge

Providing a partial Key/Value item instead of a set of operations will merge the partial Key/Value into the existing Key/Value. Read more at http://orchestrate.io/docs/apiref#keyvalue-patch

```python
response = client.patch_merge('a_collection', 'a_key', {"foo": "bar"})
# make sure the request succeeded
response.raise_for_status()
```

The optional `ref` argument can be used to perform conditional updates.
To update only if your `ref` matches the latest version's, provide it to the method:

```python
res = client.get('a_collection', 'a_key')

response = client.patch_merge('a_collection', 'a_key', {"foo": "bar"}, res.ref)
# Only merges if the response.ref is the current reference
```

To learn more about `refs`, see http://orchestrate.io/docs/apiref#refs

The `If-None-Match` header is not relevant to a `PATCH` request, since the key MUST already exist for the patch operation to succeed

This method returns a [Response](#response) object.

### Client.delete

```python
# delete an item version
client.delete('a_collection', 'a_key', 'a_ref')
# delete an item and all its versions
client.delete('a_collection', 'a_key')
# delete a collection and all its items
client.delete('a_collection')
```

Deletes a collection, item, or item version, depending on how many arguments you provide.

This method returns a [Response](#response) object.

### Client.refs

```python
refs = client.refs('a_collection', 'a_key')
# make sure the request succeeded
refs.raise_for_status()
# prints the number of versions for this item
print refs['count']
# prints every item version as a list of dicts
print refs['results']
```

Lists every version of an item.

To control which versions are passed back, you can use these keyword arguments:

* limit: the number of results to return. (default: 10, max: 100)
* offset: the starting position of the results. (default: 0)
* values: whether to return the value for each ref in the history. (default: false)

```python
refs = client.refs('a_collection', 'a_key', limit=5, values=True, offset=10)
```

This method returns a [Response](#response) object.

### Client.list

```python
# list all items in the collection
pages = client.list('a_collection')
# get the first page of items in the collection
page = pages.next()
# ensure the request succeeded
page.raise_for_status()
# get all items in the collection
items = pages.all()
# iterate over the pages of items in the collection
for page in pages:
  # ensure getting the page succeeded
  page.raise_for_response()
```

Return a [Pages](#pages) object for iterating over the contents of a collection.

To control which items are passed back, you can use these keywords:

* limit: the number of results to return. (default: 10, max: 100)
* startKey: the start of the key range to paginate from including the specified value if it exists.
* afterKey: the start of the key range to paginate from excluding the specified value if it exists.
* beforeKey: the end of the key range to paginate to excluding the specified value if it exists.
* endKey: the end of the key range to paginate to including the specified value if it exists.

```python
pages = client.list('a_collection', limit=20, startKey='a_key', endKey='another_key')
pages.next()
```

### Client.search

#### `**kwargs`

```python
# list all items that match our search query
pages = client.search('cafes', 'value.location:NEAR:{lat:... lon:... dist:1mi}',
                      sort='value.location:distance:asc')
# get the first page of items in the collection
page = pages.next()
# ensure the request succeeded
page.raise_for_status()
# get all items in the collection
items = pages.all()
# iterate over the pages of items in the collection
for page in pages:
  # ensure getting the page succeeded
  page.raise_for_response()
```

#### Using `Porc.Search`
See [Porc.Search](#search) for detailed documentation on the [`Porc.Search`](#search) API.

```python
search = porc.Search().query('value.location:NEAR:{lat:... lon:... dist:1mi}').sort('location:distance', 'asc')
# list all items that match our search query
pages = client.search('cafes', search)
# get the first page of items in the collection
page = pages.next()
# ensure the request succeeded
page.raise_for_status()
# get all items in the collection
items = pages.all()
# iterate over the pages of items in the collection
for page in pages:
  # ensure getting the page succeeded
  page.raise_for_response()
  ```

#### Response

Return a [Pages](#pages) object for iterating over the results of search queries.

The `query` parameter follows [Lucene query syntax][]. You can type out queries by hand, or use [lucene-querybuilder][] to construct them, like this:

[lucene query syntax]: http://lucene.apache.org/core/2_9_4/queryparsersyntax.html
[lucene-querybuilder]: https://pypi.python.org/pypi/lucene-querybuilder/0.1.2

```python
from porc.util import Q

query = Q('field1', 'value1') & Q('field2', 'value2') | Q('field3', 'value3')
print query
# (field1:(value1) AND field2:(value2)) field3:(value3)
pages = client.search('a_collection', query)
```

To control which items are passed back, you can use these keywords:

* limit: the number of results to return. (default: 10, max: 100)
* offset: the starting position of the results. (default: 0)

```python
pages = client.list('a_collection', 'catdog', limit=20, offset=10)
pages.next()
```

### Client.get_relations

```python
# get friends
resp = client.get_relations('a_collection', 'a_key', 'friends')
# get family of friends
resp = client.get_relations('a_collection', 'a_key', 'friends', 'family')
# get favorites of friends of family
resp = client.get_relations('a_collection', 'a_key', 'friends', 'family', 'favorites')
# ensure the request succeeded
resp.raise_for_status()
# print number of results
print resp['count']
# print results
print resp['results']
```

Returns items related to a given item along the given kinds of relationships.

This method returns a [Response](#response) object.

### Client.put_relation

```python
# create a relationship between two items
resp = client.put_relation('a_collection', 'a_key', 'friends', 'b_collection', 'b_key')
# ensure the request succeeded
resp.raise_for_status()
```

Creates a relationship between two items, which don't need to be in the same collection.

This method returns a [Response](#response) object.

### Client.delete_relation

```python
# delete a relationship between two items
resp = client.delete_relation('a_collection', 'a_key', 'friends', 'b_collection', 'b_key')
# ensure the request succeeded
resp.raise_for_status()
```

Deletes a relationship between two items, which don't need to be in the same collection.

This method returns a [Response](#response) object.

### Client.get_event

```python
# get an event
event = self.client.get_event('a_collection', 'a_key', 'a_type', 1404973704558, 4)
# ensure the request succeeded
event.raise_for_status()
# print event timestamp
print event.timestamp
# print event data
print event['a_field']
```

Gets an event.

This method returns a [Response](#response) object.

### Client.post_event

```python
# add an event; let orchestrate generate timestamp
resp = client.post_event('a_collection', 'a_key', 'a_type', {'herp': 'derp'})
# ensure request succeeded
resp.raise_for_status()
# add an event; use your own timestamp
from datetime import datetime
resp = client.post_event('a_collection', 'a_key', 'a_type', {'herp': 'derp'}, datetime.now())
# ensure the request succeeded
resp.raise_for_status()
# print the event's timestamp
print resp.timestamp
```

Create an event. You can allow Orchestrate to generate a timestamp, or provide your own as a [datetime object](https://docs.python.org/2/library/datetime.html#datetime-objects).

This method returns a [Response](#response) object.

### Client.put_event

```python
from datetime import datetime

# generate a timestamp
timestamp = datetime(1988, 8, 16)
# update an existing event
resp = client.put_event('a_collection', 'a_key', 'a_type', timestamp, 4, {'herp': 'derp'})
# ensure the update succeeded
resp.raise_for_status()
```

Update an existing event.

You can conditionally update an event only if you provide the same `ref` value as the latest version of the event, like so:

```python
resp = client.put_event('a_collection', 'a_key', 'a_type', timestamp, 4, {'herp': 'derp'}, 'a_ref')
```

This method returns a [Response](#response) object.

### Client.delete_event

```python
from datetime import datetime

# generate a timestamp
timestamp = datetime(1988, 8, 16)
# delete an existing event
resp = client.delete_event('a_collection', 'a_key', 'a_type', timestamp, 4)
# ensure the deletion succeeded
resp.raise_for_status()
```

Delete an existing event.

You can conditionally delete an event only if you provide the same `ref` value as the latest version of the event, like so:

```python
resp = client.delete_event('a_collection', 'a_key', 'a_type', timestamp, 4, 'a_ref')
```
This method returns a [Response](#response) object.

### Client.list_events

```python
# get a list
pages = client.list_events('a_collection', 'a_key', 'a_type', limit=1, afterEvent=datetime.utcfromtimestamp(0))
# get the first page of events
page = pages.next()
# ensure getting the first page succeeded
page.raise_for_status()
```

Return a [Pages](#pages) object for iterating over the results of event listings.

To control which events are passed back, you can use these keyword arguments:

* limit: the number of results to return. (default: 10, max: 100)
* startEvent: the inclusive start of a range to query. (optional)
* afterEvent: the non-inclusive start of a range to query. (optional)
* beforeEvent: the non-inclusive end of a range to query. (optional)
* endEvent: the inclusive end of a range to query. (optional)

### Client.async

```python
# add three items
with self.client.async() as c:
    # begin the requests
    futures = [
        c.post('a_collection', {"holy gosh": True}),
        c.post('a_collection', {"holy gosh": True}),
        c.post('a_collection', {"holy gosh": True})
    ]
    # block until they complete
    responses = [future.result() for future in futures]
    # ensure they succeeded
    [response.raise_for_status() for response in responses]
```

Creates an asynchronous Porc client, whose interface is identical to the synchronous version except that any method that would return a [Response](#response) instead returns a Future.

To get the Response, call `future.result`, which blocks execution until the request completes, like so:

```python
future = async_client.get('a_collection', 'a_key')
response = future.result()
response.raise_for_status()
print response.ref
# prints the item's ref value
```

### Pages

```python
# get pages
pages = client.list('a_collection')
# get page one
page = pages.next()
# get page two
page = pages.next()
# get page three
page = pages.next()
# get page two
page = pages.prev()
# reset
pages.reset()
# get page one
page = pages.next()
# get all items
items = pages.all()
```

`Pages` objects allow you to iterate through listings of items, like search query results and collection listings. They are returned automatically by any [Client](#client) methods that deal with listings.

### Pages.next

```python
# get page one
page = pages.next()
# get page two
page = pages.next()
```

Gets the next page in a listing. If there is no next page, it will raise `StopIteration`.

This method returns a [Response](#response) object.

### Pages.prev

```python
# get page one
page = pages.next()
# get page two
page = pages.next()
# get page one
page = pages.prev()
```

Get the previous page in a listing. If there is no previous page, or the given listing doesn't provide `prev` links (ex: collection listings), it will raise `StopIteration`.

This method returns a [Response](#response) object.

### Pages.reset

```python
# get page one
page = pages.next()
# get page two
page = pages.next()
# reset
pages.reset()
# get page one
page = pages.next()
```

Resets the internal mechanism used to iterate through listings.

### Pages.all

```python
# get all items in a listing
items = pages.all()
for item in items:
  print item
  # prints the item's JSON contents as a dict
```

Returns all items in a listing, rather than pages containing a subset of items.

This is a convenience method roughly equivalent to:

```python
results = []
for page in pages:
  page.raise_for_status()
  results.extend(response['results'])
return results
```

This method does NOT return [Response](#response) objects. Instead, it returns raw `dict` objects for each item.

### Patch
Convenience class to help build an *operation set* document, as required by the `HTTP PATCH` method on the Orchestrate API. The `porc.Patch.operations` attribute is a Python list containing *operations*.  An *operation* is a specification on how to mutate a JSON document on the server side. Read more about server side document operations at http://orchestrate.io/docs/apiref#keyvalue-patch

To build a patch:

```python
>>> from porc import Patch
>>> patch = Patch()
>>> patch.add("derp", True).remove("herp").decrement("foo")
<porc.patch.Patch instance at 0x1021663f8>
>>> patch.operations
[{'path': 'derp', 'value': True, 'op': 'add'}, {'path': 'herp', 'op': 'remove'}, {'path': 'foo', 'value': -1, 'op': 'inc'}]
>>>
```

A patch is meant to be handed directly to the `porc.Client.patch` method, as such:

```python
import porc
client = porc.Client("API_KEY")
patch = porc.Patch()

ref = client.head("a_collection", "a_key").ref
patch.add("derp", True).remove("herp").decrement("foo")
res = client.patch("a_collection", "a_key", patch, ref)
# Returns a Response Object
```

A Patch object can be chained together to build an *operation set*.

### Patch.add
Depending on the specified path, creates a field with that value, replaces
an existing field with the specified value, or adds the value to an array.

```python
path = "location.latitude"
value = "48.7502N"
patch = Patch()
patch.add(path, value)
```

### Patch.remove
Removes the field at a specified path

```python
path = "location.longitude"
patch.remove(path)
```

### Patch.replace
Replaces an existing value with the given value at the specified path.

```python
path = "location.latitude"
value = "48.7502N"
patch.replace(path, value)
```

### Patch.move
Moves a value from one path to another, removing the original path.

```python
old_path = "location.latitude"
new_path = "location.lat"
patch.move(old_path, new_path)
```

### Patch.copy
Copies the value at one path to another.

```python
original = "location.latitude"
copy_to = "location.lat"
patch.copy(original, copy_to)
```

### Patch.test
Tests equality of the value at a particular path to a specified value, the entire request fails if the test fails.

```python
test = "correct_value"
path = "id"
patch.test(path, test)
```

### Patch.increment
Increments the numeric value at a specified field by the given numeric value, decrements if given numeric value is negative. If no value is given, `Patch.increment` will increment the field by 1.

```python
patch.increment("problems")
patch.operations # [{'path': 'problems', 'value': 1, 'op': 'inc'}]

patch.increment("problems", 99)
patch.operations # [{'path': 'problems', 'value': 1, 'op': 'inc'}, {'path': 'problems', 'value': 99, 'op': 'inc'}]
```

### Patch.decrement
Decrements the numeric value at a specified field by given a numeric value.
This method is sugar. It wraps the `increment` method and multiplies the
value by -1. Passing in a negative value will increment the field. The
default is `-1`

```python
patch.decrement("problems")
patch.operations # [{'path': 'problems', 'value': -1, 'op': 'inc'}]

patch.decrement("problems", 99)
patch.operations # [{'path': 'problems', 'value': -1, 'op': 'inc'}, {'path': 'problems', 'value': -99, 'op': 'inc'}]
```


### Search
The `Porc.Search` class is another convenience class to help build a Lucene style query. The class supports method chaining. It's goal is to help increase the readability of Python code. To learn more about Orchestrate's querying functionality, see http://orchestrate.io/docs/apiref#search.

```python
search = porc.Search().query("price:[300000 TO 450000]").sort("price", "asc").limit("50")
pages = client.search('for_sale', search)
# get the first page of items in the collection
page = pages.next()
# ensure the request succeeded
page.raise_for_status()
# get all items in the collection
items = pages.all()
# iterate over the pages of items in the collection
for page in pages:
  # ensure getting the page succeeded
  page.raise_for_response()
```

#### Search.query
This is an essential method necessary to build a search object. It is very thin, only setting the `query` parameter. It accepts raw lucene query syntax.To learn more about Orchestrate's querying functionality, see http://orchestrate.io/docs/apiref#search.

```python
search = porc.Search().query("last_name:Smith*")
pages = client.search('users', search)
page = pages.next()
page.raise_for_status()
```

#### Search.limit
The result count limit as an integer, the default is `10` and the max is `100`.

```python
search = porc.Search().query("last_name:Smith*").limit(1)
pages = client.search('users', search)
# get all items in the collection
items = pages.all()
```

#### Search.offset
The starting position of the result set.

```python
search = porc.Search().query("last_name:Smith*").offset(2)
pages = client.search('users', search)
page = pages.next()
page.raise_for_status()
```

#### Search.aggregate
Required parameters:

 * `aggregate_type` -
 * `field` -

The `options` parameter is an optional `str` or `list` that maybe required by the `aggregate_type`.  

```python
buckets = ['*~5', '5~10', '10~30', '30~*']
search = porc.Search().query("price:[250000 TO 450000]").aggregate('distance', 'location', buckets)
pages = client.search('users', search)
page = pages.next()
page.raise_for_status()
```

#### Search.sort

```python
search = porc.Search().query("price:[250000 TO 450000]").sort("price", "desc")
pages = client.search('users', search)
page = pages.next()
page.raise_for_status()
```

### Response

```python
# get an item
item = client.get('a_collection', 'a_key')
# make sure the request succeeded
item.raise_for_status()
# prints your item's ref value
print item.ref
# prints your item's fields and values as a dict
print item.json
# prints a given field from the item's json
print item[FIELD]
```

All requests to Orchestrate come back wrapped in a Response for your ease and sanity. Responses are subclassed from [Requests Responses](http://docs.python-requests.org/en/latest/api/#requests.Response) and the [Built-In Mapping Type](https://docs.python.org/2/library/stdtypes.html#mapping-types-dict) (aka dicts), so they have all methods from both of those classes at your disposal, such as...

```python
# some methods from Python Requests
response.status_code
response.raise_for_status()
response.headers
# some methods from dict
response.keys()
response.items()
response.values()
response['field'] = 'value'
del response['field']
```

`dict`-like methods pertain to the JSON body contents of HTTP responses, stored as the `Response.json` attribute. If an HTTP response didn't have a JSON body, it defaults to `{}`.

Responses will also parse headers and urls for relevant values like refs, relation types, etc. So, depending on the request, your Response may have these attributes:

* collection
* key
* ref
* type (as in event type)
* timestamp (for events)
* ordinal (for events)
* kind (for relations)
* kinds (from Client.get_relation)

All those attributes will be strings, except for `kinds`, which is a list of strings.

## Tests

To run tests, get the source code and use `setup.py`:

    git clone git@github.com:orchestrate-io/porc.git
    cd porc
    python setup.py test

## License

[ASLv2][], yo.

[orchestrate.io]: http://orchestrate.io/
[pip]: https://pypi.python.org/pypi/pip
[ASLv2]: http://www.apache.org/licenses/LICENSE-2.0.html
