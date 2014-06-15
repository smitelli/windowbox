from __future__ import absolute_import
import pytz
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UTCDateTime(db.TypeDecorator):
    impl = db.DateTime

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.astimezone(pytz.utc)

    def process_result_value(self, value, dialect):
        if value is not None:
            return datetime(
                value.year, value.month, value.day, value.hour, value.minute,
                value.second, value.microsecond, tzinfo=pytz.utc)
