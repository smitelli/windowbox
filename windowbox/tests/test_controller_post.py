"""
Tests for the Post controller.
"""

import pytest
from unittest.mock import Mock
from windowbox.controllers.post import PostController


def test_post_message_to_post(datetime_now, db, emoji, sender_instance):
    """
    Should be able to parse a message into a Post.
    """
    message = Mock()
    message.from_address = 'known.sender@example.com'
    message.date = datetime_now
    message.x_mailer = 'pytest'
    message.text_plain = f'Today is a good day for making {emoji} Posts.'

    # Need to create a Sender for the create to succeed
    sender_instance.email_address = 'known.sender@example.com'
    db.session.add(sender_instance)

    post = PostController.message_to_post(message)

    assert post.sender == sender_instance
    assert post.created_utc == datetime_now
    assert post.user_agent == 'pytest'
    assert post.caption == f'Today is a good day for making {emoji} Posts.'

    # Unknown sender should not succeed
    message.from_address = 'unknown.sender@example.com'

    with pytest.raises(PostController.UnknownSender):
        PostController.message_to_post(message)


def test_post_get_by_id(post_instances):
    """
    Test getting one Post (and maybe its neighbors).
    """

    # Test for one Post, plus adjacent at the oldest end
    post_set = PostController.get_by_id(post_instances[0].id)
    assert post_set.older_post is None
    assert post_set.post == post_instances[0]
    assert post_set.newer_post == post_instances[1]

    # Test for one Post, plus adjacent at the oldest end
    post_set = PostController.get_by_id(post_instances[-1].id)
    assert post_set.older_post == post_instances[-2]
    assert post_set.post == post_instances[-1]
    assert post_set.newer_post is None

    # Test for one Post, plus adjacent in the middle somewhere
    post_set = PostController.get_by_id(post_instances[6].id)
    assert post_set.older_post == post_instances[5]
    assert post_set.post == post_instances[6]
    assert post_set.newer_post == post_instances[7]

    # Test for one Post without adjacent
    post_set = PostController.get_by_id(post_instances[6].id, include_adjacent=False)
    assert post_set.older_post is None
    assert post_set.post == post_instances[6]
    assert post_set.newer_post is None

    # Test for missing Post
    with pytest.raises(PostController.NoResultFound):
        PostController.get_by_id(666666)


def test_post_parse_query_args():
    """
    Test query argument parsing and validation.
    """
    assert PostController.parse_query_args(
        since_id=None, until_id=None, limit=None) == {
            'since_id': None, 'until_id': None, 'limit': None}

    assert PostController.parse_query_args(
        since_id='1', until_id=None, limit=None) == {
            'since_id': 1, 'until_id': None, 'limit': None}

    assert PostController.parse_query_args(
        since_id=None, until_id='2', limit=None) == {
            'since_id': None, 'until_id': 2, 'limit': None}

    assert PostController.parse_query_args(
        since_id=None, until_id=None, limit='3') == {
            'since_id': None, 'until_id': None, 'limit': 3}

    # Args must be parsable as ints
    with pytest.raises(PostController.InvalidArgument):
        PostController.parse_query_args(since_id='wrong', until_id=None, limit=None)
    with pytest.raises(PostController.InvalidArgument):
        PostController.parse_query_args(since_id=None, until_id='wrong', limit=None)
    with pytest.raises(PostController.InvalidArgument):
        PostController.parse_query_args(since_id=None, until_id=None, limit='wrong')

    # Since *and* until are invalid together
    with pytest.raises(PostController.InvalidArgument):
        PostController.parse_query_args(since_id='0', until_id='34', limit=None)

    # Limit must be in the valid range
    with pytest.raises(PostController.InvalidArgument):
        PostController.parse_query_args(since_id=None, until_id=None, limit='-1')
    with pytest.raises(PostController.InvalidArgument):
        PostController.parse_query_args(since_id=None, until_id=None, limit='101')


def test_post_get_many(post_instances):
    """
    Should be able to return slices of Posts with required pagination flags.
    """

    # Test getting *everything*
    post_set = PostController.get_many()
    assert len(post_set.posts) == 12
    assert not post_set.has_more
    assert post_set.page_mode == PostController.PAGE_MODE.UNTIL

    # Test getting all posts since x; verify the ordering
    post_set = PostController.get_many(since_id=post_instances[3].id)
    last_id = post_instances[3].id
    last_date = post_instances[3].created_utc
    for p in post_set.posts:
        assert p.id > last_id
        assert p.created_utc > last_date
        last_id = p.id
        last_date = p.created_utc
    assert post_set.page_mode == PostController.PAGE_MODE.SINCE

    # Test getting all posts until x; verify the ordering
    post_set = PostController.get_many(until_id=post_instances[-3].id)
    last_id = post_instances[-3].id
    last_date = post_instances[-3].created_utc
    for p in post_set.posts:
        assert p.id < last_id
        assert p.created_utc < last_date
        last_id = p.id
        last_date = p.created_utc
    assert post_set.page_mode == PostController.PAGE_MODE.UNTIL

    # Walk pagination in "until" mode
    post_set = PostController.get_many(limit=5)
    assert len(post_set.posts) == 5
    assert post_set.has_more
    post_set = PostController.get_many(until_id=post_set.posts[-1].id, limit=5)
    assert len(post_set.posts) == 5
    assert post_set.has_more
    post_set = PostController.get_many(until_id=post_set.posts[-1].id, limit=5)
    assert len(post_set.posts) == 2
    assert not post_set.has_more

    # Walk pagination in "since" mode
    post_set = PostController.get_many(since_id=0, limit=5)
    assert len(post_set.posts) == 5
    assert post_set.has_more
    post_set = PostController.get_many(since_id=post_set.posts[-1].id, limit=5)
    assert len(post_set.posts) == 5
    assert post_set.has_more
    post_set = PostController.get_many(since_id=post_set.posts[-1].id, limit=5)
    assert len(post_set.posts) == 2
    assert not post_set.has_more


def test_post_get_lastmod_datetime(datetime_now, db, post_instances):
    """
    Should return "basically now" as the lastmod date if there are no Posts.
    """
    dt = PostController.get_lastmod_datetime()

    assert dt == post_instances[-1].created_utc


def test_post_get_lastmod_datetime_empty(datetime_now, db):
    """
    Should return "basically now" as the lastmod date if there are no Posts.
    """
    dt = PostController.get_lastmod_datetime()

    assert (dt - datetime_now).total_seconds() < 1


def test_post_yield_all(post_instances):
    """
    Should be able to yield all the Posts in descending order.
    """
    assert [*PostController.yield_all()] == [*reversed(post_instances)]


def test_post_yield_unbarked(post_instances):
    """
    Should be able to yield all the "unbarked" Posts in ascending order.
    """
    assert [*PostController.yield_unbarked()] == post_instances

    for p in post_instances:
        p.is_barked = True

    assert [*PostController.yield_unbarked()] == []
