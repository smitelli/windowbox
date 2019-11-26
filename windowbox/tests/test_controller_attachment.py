"""
Tests for the Attachment controller.
"""

import pytest
from unittest.mock import patch
from windowbox.controllers.attachment import AttachmentController
from windowbox.models.attachment import Dimensions


def test_attachment_message_to_data():
    """
    Should yield data for known message parts in a predictable order.
    """

    class MockMessage:
        """
        Fake Message class with a couple of known and unknown types.
        """
        part_types = {'image/png', 'image/jpeg', 'application/pdf'}
        part_data = {
            'application/pdf': [b'pdf1', b'pdf2', b'pdf3'],
            'image/jpeg': [b'jpg1', b'jpg2', b'jpg3'],
            'image/png': [b'png1', b'png2', b'png3']}

        def yield_parts(self, mime_type):
            yield from self.part_data[mime_type]

    assert [*AttachmentController.message_to_data(MockMessage())] == [
        ('image/jpeg', b'jpg1'),
        ('image/jpeg', b'jpg2'),
        ('image/jpeg', b'jpg3'),
        ('image/png', b'png1'),
        ('image/png', b'png2'),
        ('image/png', b'png3')]


def test_attachment_get_by_id(db, attachment_instance):
    """
    Should be able to get a single attachment instance.
    """
    db.session.add(attachment_instance)
    db.session.flush()

    att = AttachmentController.get_by_id(attachment_instance.id)

    assert att == attachment_instance

    with pytest.raises(AttachmentController.NoResultFound):
        AttachmentController.get_by_id(666666)


def test_attachment_decode_dimensions():
    """
    Whale on the dimensions decoder regex.
    """
    assert AttachmentController.decode_dimensions('full') == (None, None, False)
    assert AttachmentController.decode_dimensions('100x') == (100, None, True)
    assert AttachmentController.decode_dimensions('100~') == (100, None, False)
    assert AttachmentController.decode_dimensions('x200') == (None, 200, True)
    assert AttachmentController.decode_dimensions('~200') == (None, 200, False)
    assert AttachmentController.decode_dimensions('100x200') == (100, 200, True)
    assert AttachmentController.decode_dimensions('100~200') == (100, 200, False)

    assert AttachmentController.decode_dimensions('full.ext') == (None, None, False)
    assert AttachmentController.decode_dimensions('100x.ext') == (100, None, True)
    assert AttachmentController.decode_dimensions('100~.ext') == (100, None, False)
    assert AttachmentController.decode_dimensions('x200.ext') == (None, 200, True)
    assert AttachmentController.decode_dimensions('~200.ext') == (None, 200, False)
    assert AttachmentController.decode_dimensions('100x200.ext') == (100, 200, True)
    assert AttachmentController.decode_dimensions('100~200.ext') == (100, 200, False)

    assert AttachmentController.decode_dimensions('crap') is None
    assert AttachmentController.decode_dimensions('x') is None
    assert AttachmentController.decode_dimensions('~') is None

    assert AttachmentController.decode_dimensions('crap.ext') is None
    assert AttachmentController.decode_dimensions('x.ext') is None
    assert AttachmentController.decode_dimensions('~.ext') is None


def test_attachment_get_attachment_derivative(db, attachment_instance):
    """
    Should be able to turn an Attachment ID/dimensions pair into a Derivative.
    """
    db.session.add(attachment_instance)
    db.session.flush()

    expect_dv = object()

    with patch(
            'windowbox.controllers.attachment.AttachmentController.make_or_get_derivative') \
            as mock_mogd:
        mock_mogd.return_value = expect_dv

        assert AttachmentController.get_attachment_derivative(
            attachment_id=attachment_instance.id, dimensions='960~720') == expect_dv
        mock_mogd.assert_called_with(
            attachment=attachment_instance, dim_tuple=(960, 720, False))

    # Invalid dimensions should raise
    with pytest.raises(AttachmentController.NoResultFound):
        AttachmentController.get_attachment_derivative(
            attachment_id=attachment_instance.id, dimensions='not valid')

    # Valid but non-whitelisted dimensions should raise
    with pytest.raises(AttachmentController.NoResultFound):
        AttachmentController.get_attachment_derivative(
            attachment_id=attachment_instance.id, dimensions='10000x10000')


def test_attachment_make_or_get_derivative(db, attachment_instance):
    """
    Should be able to make and get a Derivative on an Attachment.
    """
    db.session.add(attachment_instance)

    with patch('windowbox.models.derivative.Derivative.ensure_storage_data') as mock_esd:
        # First iteration should make, second should get
        for _ in range(2):
            dv = AttachmentController.make_or_get_derivative(
                attachment=attachment_instance,
                dim_tuple=Dimensions(100, 75, True))

            assert dv.attachment == attachment_instance
            assert dv.mime_type == attachment_instance.mime_type
            assert dv.width == 100
            assert dv.height == 75
            assert dv.allow_crop
            assert dv.base_path is not None
            mock_esd.assert_called()
            mock_esd.reset_mock()
