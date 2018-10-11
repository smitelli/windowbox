from __future__ import absolute_import
import pytz
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import DATETIME

db = SQLAlchemy()


class UTCDateTime(db.TypeDecorator):
    impl = DATETIME

    def __init__(self, *args, **kwargs):
        # kwargs['fsp'] = 6

        super(UTCDateTime, self).__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.astimezone(pytz.utc).replace(tzinfo=None)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.replace(tzinfo=pytz.utc)

        return value
