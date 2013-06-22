import json
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from windowbox.configs.base import DATABASE_CONFIG

_engine = sa.create_engine(DATABASE_CONFIG['URI'], **DATABASE_CONFIG['KWARGS'])
DeclarativeBase = declarative_base(bind=_engine)
session = sa.orm.sessionmaker(bind=_engine, autocommit=False, autoflush=False)()


class JSONEncodedDict(sa.types.TypeDecorator):
    impl = sa.types.Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
