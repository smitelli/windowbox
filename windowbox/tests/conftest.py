"""
Test fixtures for pytest.

Attributes:
    TEST_DB_SUFFIX: The expected value the database connection string should end
        with. If this suffix does not match, all tests that use a database
        fixture will abort for safety.
"""

import pytest
from datetime import datetime, timezone
from windowbox import app as test_app
from windowbox.database import db as test_db
from windowbox.models.attachment import Attachment
from windowbox.models.post import Post
from windowbox.models.sender import Sender

TEST_DB_SUFFIX = '/test.sqlite'


@pytest.fixture(scope='session')
def app():
    """
    Return the Windowbox Flask application.
    """
    return test_app


@pytest.fixture
def client(app):
    """
    Return a Flask test client configured for the Windowbox application.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture
def db(app):
    """
    Return a fresh, empty test database.

    This requires the test configuration specifies a database URI which has a
    test-like suffix. This is to protect against accidentally clobbering a real
    database.

    The test database is completely cleared at the end of each test function.
    """
    if not app.config['SQLALCHEMY_DATABASE_URI'].endswith(TEST_DB_SUFFIX):  # pragma: nocover
        raise EnvironmentError('Refusing to test a non-test database')

    with app.app_context():
        test_db.create_all()

        yield test_db

        test_db.session.rollback()  # in case of sloppy tests
        test_db.drop_all()


@pytest.fixture
def attachment_instance(post_instance):
    """
    Return an instance of Attachment that the database will accept.
    """
    return Attachment(
        post=post_instance,
        mime_type='image/jpeg')


@pytest.fixture
def post_instance(sender_instance):
    """
    Return an instance of Post that the database will accept.
    """
    return Post(
        sender=sender_instance,
        caption='Post Fixture')


@pytest.fixture
def post_instances(app, db, png_pixel, sender_instance):
    """
    Return 12 instances of Post, some with Attachments, flushed to the database.

    Post IDs should increase monotonically. The dates should also all make
    logical sense, with one calendar month separating each instance. The list of
    all Posts is returned by the fixture, but it may not be needed in some test
    contexts -- the mere act of including the fixture will create the Posts.

    Even-indexed Posts will have attachments. This is to ensure tests have
    adequate coverage for both regular and Attachment-less Posts.
    """
    posts = []

    for i in range(12):
        index = i + 1
        post = Post(
            sender=sender_instance,
            caption=f'Post Fixture {index}',
            created_utc=datetime(2018, index, 1, 0, 0, 0, tzinfo=timezone.utc))
        db.session.add(post)
        posts.append(post)

        if index % 2 == 0:
            attachment = Attachment(
                base_path=app.attachments_path, mime_type='image/png')
            post.attachments.append(attachment)

            db.session.flush()
            attachment.set_storage_data(png_pixel)

    db.session.flush()

    return posts


@pytest.fixture
def sender_instance():
    """
    Return an instance of Sender that the database will accept.
    """
    return Sender(
        email_address='sender.fixture@example.com',
        display_name='Sender Fixture')


@pytest.fixture
def datetime_now():
    """
    Return "now" as a timezone-aware datetime in UTC.
    """
    return datetime.now(tz=timezone.utc)


@pytest.fixture(scope='session')
def emoji():
    """
    Return a few emoji from Unicode plane 1.

    This is to smoke-test data conversion functions to make sure they're not
    inappropriately encoding to an undesirable character set.
    """
    return u'\U0001F32E\U0001F4A9\U0001F756\U0001F32F\U0001F37B'


@pytest.fixture(scope='session')
def png_pixel():
    """
    Return data for a 1x1 PNG containing a single #ff0000 pixel.
    """
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf'
        b'\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xae'
        b'B`\x82')
