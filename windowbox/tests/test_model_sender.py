"""
Tests for the Sender model.
"""

import pytest
import sqlalchemy.exc
from windowbox.models.sender import Sender


def test_sender_storage(db, datetime_now, emoji):
    """
    Should be able to save a Sender then re-read it verbatim.
    """
    assume_id = 1
    created_utc = datetime_now
    email_address = f'test.{emoji}@example.com'
    display_name = f'Test Sender {emoji}'

    in_sender = Sender(
        created_utc=created_utc,
        email_address=email_address,
        display_name=display_name)
    db.session.add(in_sender)
    db.session.flush()

    out_sender = Sender.query.filter_by(id=assume_id).one()

    assert out_sender.id == assume_id
    assert out_sender.created_utc == created_utc
    assert out_sender.email_address == email_address
    assert out_sender.display_name == display_name


def test_sender_email_address_unique(db):
    """
    Should not be able to create two Senders with conflicting email_address.
    """
    sender1 = Sender(
        email_address='conflict@example.com',
        display_name='Sender 1')
    db.session.add(sender1)
    db.session.flush()

    sender2 = Sender(
        email_address='conflict@example.com',
        display_name='Sender 2')
    db.session.add(sender2)

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.flush()


def test_sender_email_address_ci(db, sender_instance):
    """
    Should be able to look up a Sender by email_address regardless of case.
    """
    sender_instance.email_address = 'Look.Me.Up@Example.COM'
    db.session.add(sender_instance)
    db.session.flush()

    assert Sender.query.filter_by(email_address='look.me.up@example.com').one()
    assert Sender.query.filter_by(email_address='LOOK.ME.UP@EXAMPLE.COM').one()
