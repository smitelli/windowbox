from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from windowboxconfig import DATABASE_CONFIG

engine = create_engine(DATABASE_CONFIG['URI'], **DATABASE_CONFIG['KWARGS'])
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

sess = scoped_session(Session)

# Following classes copied from SQLAlchemy docs (examples/vertical/dictlike.py)
class VerticalProperty(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return '<%s %r=%r>' % (self.__class__.__name__, self.key, self.value)


class VerticalPropertyDictMixin(object):
    _property_type = VerticalProperty
    _property_mapping = None

    __map = property(lambda self: getattr(self, self._property_mapping))

    def __getitem__(self, key):
        return self.__map[key].value

    def __setitem__(self, key, value):
        property = self.__map.get(key, None)
        if property is None:
            self.__map[key] = self._property_type(key, value)
        else:
            property.value = value

    def __delitem__(self, key):
        del self.__map[key]

    def __contains__(self, key):
        return key in self.__map

    def keys(self):
        return self.__map.keys()

    def values(self):
        return [prop.value for prop in self.__map.values()]

    def items(self):
        return [(key, prop.value) for key, prop in self.__map.items()]

    def __iter__(self):
        return iter(self.keys())
