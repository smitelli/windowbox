"""
Tests for the custom database types.
"""

from datetime import datetime, timedelta, timezone


def test_utc_datetime_constructor(db):
    """
    Verify the fractional seconds part has the expected value of 6.
    """
    assert db.UTCDateTime().fsp == 6


def test_utc_datetime_save(db):
    """
    Test saving arbitrary datetimes as timezone-naive UTC.
    """
    now_utc_naive = datetime.now()
    now_utc_aware = now_utc_naive.replace(tzinfo=timezone.utc)
    now_est_aware = now_utc_aware.astimezone(timezone(timedelta(hours=-5)))

    utc = db.UTCDateTime()

    # None is not adjusted
    assert utc.process_bind_param(None, None) is None

    # Naive datetimes should work, and be preserved literally
    assert utc.process_bind_param(now_utc_naive, None) == now_utc_naive

    # Aware UTC should become naive UTC
    assert utc.process_bind_param(now_utc_aware, None) == now_utc_naive

    # Aware non-UTC should become naive UTC
    assert utc.process_bind_param(now_est_aware, None) == now_utc_naive


def test_utc_datetime_load(db):
    """
    Test loading arbitrary timezone-naive datetimes.
    """
    now_utc_naive = datetime.now()
    now_utc_aware = now_utc_naive.replace(tzinfo=timezone.utc)

    utc = db.UTCDateTime()

    # None is not adjusted
    assert utc.process_result_value(None, None) is None

    # All incoming datetimes should become aware UTC with the same value
    assert utc.process_result_value(now_utc_naive, None) == now_utc_aware
