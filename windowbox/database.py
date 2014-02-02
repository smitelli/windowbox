import pytz
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from windowbox.configs.base import DATABASE_CONFIG

_engine = sa.create_engine(DATABASE_CONFIG['URI'], **DATABASE_CONFIG['KWARGS'])
DeclarativeBase = declarative_base(bind=_engine)
session = sa.orm.sessionmaker(bind=_engine, autocommit=False, autoflush=False)()


class UTCDateTime(sa.types.TypeDecorator):
    impl = sa.types.DateTime

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.astimezone(pytz.UTC)

    def process_result_value(self, value, dialect):
        if value is not None:
            return datetime(value.year, value.month, value.day,
                            value.hour, value.minute, value.second,
                            value.microsecond, tzinfo=pytz.UTC)
