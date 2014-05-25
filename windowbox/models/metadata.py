from collections import defaultdict


class Metadata(object):
    def __init__(self, attributes=None):
        self.sections = defaultdict(MetadataSection)

        if attributes:
            self.parse_attributes(attributes)

    def parse_attributes(self, attributes):
        for key, data in attributes.iteritems():
            section_key = key.split('.')[0]

            self.sections[section_key].set_property(key, data)


class MetadataSection(object):
    def __init__(self):
        self.items = defaultdict(MetadataItem)

    def set_property(self, key, data):
        parts = key.split('.')
        kind = parts.pop(-1)
        item_key = '.'.join(parts)

        self.items[item_key].set_property(kind, data)


class MetadataItem(object):
    def __init__(self, description=None, number=None, value=None):
        self.description = description
        self.number = number
        self.value = value

    def set_property(self, kind, data):
        if kind == 'desc':
            self.description = data
        elif kind == 'num':
            self.number = data
        elif kind == 'val':
            self.value = data
        else:
            raise AttributeError
