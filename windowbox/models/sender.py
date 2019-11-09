"""
Sender model.
"""

from windowbox.database import db


class Sender(db.Model):
    """
    Sender model.

    A Sender is the author and owner of a Post.

    Attributes:
        EMAIL_ADDRESS_LENGTH: The maximum size of the email_address column.
        DISPLAY_NAME_LENGTH The maximum size of the display_name column.
    """

    EMAIL_ADDRESS_LENGTH = 255
    DISPLAY_NAME_LENGTH = 255

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    email_address = db.Column(
        db.Unicode(length=EMAIL_ADDRESS_LENGTH, collation='NOCASE'),
        nullable=False, unique=True)
    created_utc = db.Column(db.UTCDateTime, nullable=False, server_default=db.func.now(6))
    display_name = db.Column(db.Unicode(length=DISPLAY_NAME_LENGTH), nullable=False)
