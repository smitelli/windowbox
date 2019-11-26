"""
Tests for the Post model.
"""

from windowbox.models.attachment import Attachment
from windowbox.models.post import Post


def test_post_storage(db, datetime_now, emoji, sender_instance):
    """
    Should be able to save a Post then re-read it verbatim.
    """
    assume_id = 1
    sender = sender_instance
    created_utc = datetime_now
    caption = f'Hello from pytest! {emoji}'
    user_agent = f'Some UA {emoji}'
    is_barked = True

    in_post = Post(
        sender=sender,
        created_utc=created_utc,
        caption=caption,
        user_agent=user_agent,
        is_barked=is_barked)
    db.session.add(in_post)
    db.session.flush()

    out_post = Post.query.filter_by(id=assume_id).one()

    assert out_post.id == assume_id
    assert out_post.sender == sender
    assert out_post.created_utc == created_utc
    assert out_post.caption == caption
    assert out_post.user_agent == user_agent
    assert out_post.is_barked == is_barked


def test_post_has_attachment():
    """
    Should be able to tell if it has an Attachment or not.
    """
    p = Post()
    assert not p.has_attachment

    p.attachments.append(Attachment())
    assert p.has_attachment


def test_post_top_attachment():
    """
    Should be able to return the "top" Attachment.

    Note that once this is rebuilt from a DB load, the ordering of attachments
    is not well-defined.
    """
    p = Post()
    a1 = Attachment()
    a2 = Attachment()
    a3 = Attachment()

    p.attachments = [a1, a2, a3]
    assert p.top_attachment is a1


def test_post_new_attachment():
    """
    Should be able to construct an Attachment with correct linkage to Post.
    """
    p = Post()
    a = p.new_attachment(mime_type='application/testing')

    assert a.post is p
    assert a.mime_type == 'application/testing'


def test_post_set_stripped_caption():
    """
    Should correctly sanitize and strip caption text.
    """
    p = Post()

    p.set_stripped_caption('test')
    assert p.caption == 'test'

    p.set_stripped_caption('''This has a signature.

-----
Scott Smitelli
<scott@example.com>
https://www.scottsmitelli.com/
''')
    assert p.caption == 'This has a signature.'

    p.set_stripped_caption('This has\n\n\n\n\n\n\n\n\n\n\n\nexcessive\n\n\n\n\nnewlines.')
    assert p.caption == 'This has\n\nexcessive\n\nnewlines.'

    p.set_stripped_caption('    \n   This has whitespace.  \t   ')
    assert p.caption == 'This has whitespace.'
