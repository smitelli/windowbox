"""
Tests for the console scripts.
"""

from unittest.mock import Mock, patch
from windowbox import app
from windowbox.bark import main as main_bark, run_bark
from windowbox.fetch import main as main_fetch, run_fetch
from windowbox.clients.imap import NoMessages
from windowbox.controllers.post import PostController


def test_main_bark():
    """
    Verify the main function for the bark script dispatches as expected.
    """
    with patch('windowbox.bark.run_bark') as mock_run_bark:
        assert main_bark() == 0

    mock_run_bark.assert_called_with(twitter_client=app.twitter_client)


def test_run_bark(app, db, post_instance):
    """
    Should be able to bark a Post, or no-op if there are none ready.
    """
    app.config['SERVER_NAME'] = 'pytest-host'

    db.session.add(post_instance)
    db.session.flush()

    mock_twitter = Mock()
    mock_twitter.status_length = 280
    mock_twitter.url_length = 23

    with patch('windowbox.controllers.post.PostController.yield_unbarked') as mock_yu:
        # Try no-Posts case
        mock_yu.return_value = []
        run_bark(twitter_client=mock_twitter)

        # Try with a Post
        mock_yu.return_value = [post_instance]
        assert not post_instance.is_barked
        with app.app_context():
            run_bark(twitter_client=mock_twitter)
            assert post_instance.is_barked
        mock_twitter.update_status.assert_called_with(
            f'{post_instance.caption} http://pytest-host/post/{post_instance.id}')


def test_main_fetch():
    """
    Verify the main function for the fetch script dispatches as expected.
    """
    with patch('windowbox.fetch.run_fetch') as mock_run_fetch:
        assert main_fetch() == 0

    mock_run_fetch.assert_called_with(
        attachments_path=app.attachments_path,
        exiftool_client=app.exiftool_client,
        gmapi_client=app.gmapi_client,
        imap_client=app.imap_client)


def test_run_fetch_empty():
    """
    Should not do anything unpleasant if there are no messages.
    """
    mock_imap = Mock()
    mock_imap.yield_messages.side_effect = NoMessages

    run_fetch(
        attachments_path=None,
        exiftool_client=None,
        gmapi_client=None,
        imap_client=mock_imap)


def test_run_fetch_unknown_sender():
    """
    Should delete any and all messages from unknown senders.
    """
    msg1 = Mock(uid=b'1')
    msg2 = Mock(uid=b'2')
    msg3 = Mock(uid=b'3')

    mock_imap = Mock()
    mock_imap.yield_messages.return_value = [msg1, msg2, msg3]

    with patch(
            'windowbox.controllers.post.PostController.message_to_post',
            side_effect=PostController.UnknownSender):
        run_fetch(
            attachments_path=None,
            exiftool_client=None,
            gmapi_client=None,
            imap_client=mock_imap)

    msg1.delete.assert_called()
    msg2.delete.assert_called()
    msg3.delete.assert_called()


def test_run_fetch(db, tmp_path, post_instance):
    """
    Should fetch all messages.

    This is not really a great test, but as long as it makes it through three
    iterations and reaches the end of each (where the message is deleted)
    without raising it is probably working well enough.
    """
    msg1 = Mock(uid=b'1')
    msg2 = Mock(uid=b'2')
    msg3 = Mock(uid=b'3')

    mock_imap = Mock()
    mock_imap.yield_messages.return_value = [msg1, msg2, msg3]

    mock_exiftool = Mock()
    mock_exiftool.read_file.return_value = {}

    with patch(
            'windowbox.controllers.post.PostController.message_to_post',
            return_value=post_instance):
        with patch(
                'windowbox.controllers.attachment.AttachmentController.message_to_data',
                return_value=[('image/jpeg', b'pretend-this-is-image-data')]):
            run_fetch(
                attachments_path=tmp_path,
                exiftool_client=mock_exiftool,
                gmapi_client=Mock(),
                imap_client=mock_imap)

    msg1.delete.assert_called()
    msg2.delete.assert_called()
    msg3.delete.assert_called()
