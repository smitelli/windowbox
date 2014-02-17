import pytz
import sqlalchemy as sa
import sqlalchemy.orm as orm
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from windowbox.configs.base import DATABASE_URI, DATABASE_KWARGS

_engine = sa.create_engine(DATABASE_URI, **DATABASE_KWARGS)

DeclarativeBase = declarative_base(bind=_engine)

session = orm.sessionmaker(bind=_engine, autocommit=False, autoflush=False)()


class UTCDateTime(sa.types.TypeDecorator):
    impl = sa.types.DateTime

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.astimezone(pytz.utc)

    def process_result_value(self, value, dialect):
        if value is not None:
            return datetime(
                value.year, value.month, value.day, value.hour, value.minute,
                value.second, value.microsecond, tzinfo=pytz.utc)
