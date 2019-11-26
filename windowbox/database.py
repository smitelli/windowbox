"""
Database connection and custom column types.

Attributes:
    db: The global Flask-SQLAlchemy database object for the rest of the app and
        its models.
"""

from datetime import timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import DATETIME

db = SQLAlchemy()


class UTCDateTime(db.TypeDecorator):
    """
    Variant of DATETIME that saves values as UTC with fractional seconds.

    This is MySQL/MariaDB-specific!
    """
    impl = DATETIME

    def __init__(self, *args, **kwargs):
        """
        Constructor; always forces the "fractional seconds part" to 6.
        """
        kwargs['fsp'] = 6

        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        """
        Process values being written to the database.

        This method accepts any timezone-aware datetime, adjusts it to UTC, then
        returns a timezone-naive datetime which is understood to be UTC.
        """
        if value is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)

        return value

    def process_result_value(self, value, dialect):
        """
        Process values being read from the database.

        This method accepts a timezone-naive datetime which is assumed to be
        UTC, then returns a timezone-aware datetime with the original value.
        """
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)

        return value


db.UTCDateTime = UTCDateTime
