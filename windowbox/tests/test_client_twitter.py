"""
Tests for the Twitter API client.
"""

import pytest
from unittest.mock import Mock
from windowbox.clients.twitter import TwitterClient


@pytest.fixture
def twitter():
    """
    Return a Twitter API client.
    """
    return TwitterClient(
        consumer_key='consumerkey4twitter',
        consumer_secret='consumersecret4twitter',
        access_token='accesstoken4twitter',
        access_token_secret='accesstokensecret4twitter',
        status_length=140,  # we're old school like that
        url_length=30,
        timeout=15)


def test_constructor(twitter):
    """
    Should accept and store all publicly-defined attributes.
    """
    assert twitter.consumer_key == 'consumerkey4twitter'
    assert twitter.consumer_secret == 'consumersecret4twitter'
    assert twitter.access_token == 'accesstoken4twitter'
    assert twitter.access_token_secret == 'accesstokensecret4twitter'
    assert twitter.status_length == 140
    assert twitter.url_length == 30
    assert twitter.timeout == 15
    assert twitter.client is None


def test_make_client(twitter):
    """
    Should call the _make_client() method on first use.
    """
    client = twitter._make_client()

    assert client.auth.consumer_key == 'consumerkey4twitter'
    assert client.auth.consumer_secret == 'consumersecret4twitter'
    assert client.auth.access_token == 'accesstoken4twitter'
    assert client.auth.access_token_secret == 'accesstokensecret4twitter'
    assert client.timeout == 15


def test_update_status(twitter):
    """
    Should send tweets to Twitter.
    """
    mock_client = Mock()
    twitter._make_client = Mock(return_value=mock_client)

    twitter.update_status('Knock knock')

    twitter._make_client.assert_called()
    mock_client.update_status.assert_called_once_with(
        status='Knock knock', enable_dmcommands=False)
