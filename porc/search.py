class Search:
    def __init__(self):
        self.params = {}

    def limit(self, limit):
        self.params['limit'] = limit
        return self

    def offset(self, offset):
        self.params['offset'] = offset
        return self

    def aggregate(self, aggregate_type, field, options=None):
        aggregate = "value.%s:%s" % (field, aggregate_type)

        if type(options) is list:
            aggregate += ":%s" % ':'.join(options)
        elif type(options) is str:
            aggregate += ":%s" % options

        if 'aggregate' in self.params:
            self.params['aggregate'] = ','.join([self.params['aggregate'], aggregate])
        else:
            self.params['aggregate'] = aggregate

        return self

    def sort(self, field, order):
        sort = "value.%s:%s" % (field, order)

        if 'sort' in self.params:
            self.params['sort'] = ','.join([self.params['sort'], sort])
        else:
            self.params['sort'] = sort

        return self

    def query(self, query):
        self.params['query'] = query
        return self
