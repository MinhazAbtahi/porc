import porc
import unittest

class SearchTest(unittest.TestCase):

    def setUp(self):
        self.search = porc.Search()

    def test_limit(self):
        limit = 3
        search = self.search.limit(limit)
        assert search.params['limit'] == limit

    def test_offset(self):
        offset = 1
        search = self.search.offset(offset)
        assert search.params['offset'] == offset

    def test_aggregate(self):
        field = "foo"
        aggregates = {
            'stats': None,
            'range': ['*~5','5~10'],
            'distance': '*~1',
            'time_series': 'year'
        }

        for aggregate_type, option in aggregates.items():
            self.search = self.search.aggregate(aggregate_type, field, option)

        expected = "value.foo:stats,value.foo:range:*~5:5~10,value.foo:distance:*~1,value.foo:time_series:year"
        assert sorted(self.search.params['aggregate'].split(',')) == sorted(expected.split(','))

    def test_sort(self):
        field = "foo"
        directions = ["desc", "asc"]
        for order in directions:
            search = self.search.sort(field, order)

        expected = "value.foo:desc,value.foo:asc"
        assert self.search.params['sort'] == expected

    def test_query(self):
        query = "value.foo:[0 TO 60]"
        self.search = self.search.query(query)
        assert self.search.params['query'] == query
