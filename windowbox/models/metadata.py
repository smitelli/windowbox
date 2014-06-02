from collections import defaultdict


class Metadata(object):
    def __init__(self, attributes):
        self.items = defaultdict(MetadataItem)

        for key, data in attributes.iteritems():
            item_key, kind = key.rsplit('.', 1)
            self.items[item_key].add_data(kind, data)

        for key, item in self.items.iteritems():
            item.key = key

    def __getitem__(self, item_key):
        try:
            return self.items[item_key]
        except KeyError:
            return None


class MetadataItem(object):
    def __init__(self):
        self.key = None
        self.description = None
        self.raw_value = None
        self.value = None

    def __repr__(self):
        return '<{} key={}>'.format(self.__class__.__name__, self.key)

    def add_data(self, kind, data):
        if kind == 'desc':
            self.description = data
        elif kind == 'num':
            self.raw_value = data
        elif kind == 'val':
            self.value = data
        else:
            raise AttributeError

    def is_built(self):
        if not (self.description or self.key):
            return False
        elif not (self.value or self.raw_value):
            return False
        else:
            return True

    @property
    def display_name(self):
        return self.description or '<{}>'.format(self.key)

    @property
    def display_value(self):
        return self.value or '<{}>'.format(self.raw_value)
