"""
Tests for the Derivative model.
"""

import io
import pytest
import sqlalchemy.exc
from PIL import Image
from unittest.mock import Mock, PropertyMock, patch
from windowbox.models.derivative import Derivative


@pytest.fixture
def attachment_instance_with_data(attachment_instance):
    """
    Return an Attachment instance backed by a PNG fixture image.

    The image is a 100x76 PNG with four solid color quadrants: #FF0000 in the
    top left, #00FF00 in the top right, #0000FF in the bottom left, and #000000
    in the bottom right.
    """
    png_fh = io.BytesIO(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00L\x02\x03"
        b"\x00\x00\x00\xe6s\xfa\x9c\x00\x00\x00\x0cPLTE\x00\x00\x00\x00\x00\xff"
        b"\x00\xff\x00\xff\x00\x00\xd3#\x8e\xc7\x00\x00\x00'IDATx^c\xf8\x8f\x04"
        b"~\xadB\x02CZfTfTfT&\x14\t\x040 \x81\xa1,3*3*3*\x03\x00A\xaf\xbd\x9a=4"
        b"\xa3\x19\x00\x00\x00\x00IEND\xaeB`\x82")

    attachment_instance.get_storage_data_as_image = Mock(
        return_value=Image.open(png_fh))

    return attachment_instance


def test_derivative_storage(db, attachment_instance):
    """
    Should be able to save a Derivative then re-read it verbatim.
    """
    assume_id = 1
    attachment = attachment_instance
    mime_type = attachment_instance.mime_type
    width = 654
    height = 321
    allow_crop = True

    in_derivative = Derivative(
        attachment=attachment,
        width=width,
        height=height,
        allow_crop=allow_crop,
        mime_type=mime_type)
    db.session.add(in_derivative)
    db.session.flush()

    out_derivative = Derivative.query.filter_by(id=assume_id).one()

    assert out_derivative.id == assume_id
    assert out_derivative.attachment == attachment
    assert out_derivative.width == width
    assert out_derivative.height == height
    assert out_derivative.allow_crop == allow_crop
    assert out_derivative.mime_type == mime_type


def test_derivative_attachment_id_dimensions_unique(db, attachment_instance):
    """
    Should not be able to create two Derivatives with conflicting dimensions.
    """
    derivative1 = Derivative(
        attachment=attachment_instance,
        mime_type=attachment_instance.mime_type,
        width=1000,
        height=750,
        allow_crop=True)
    db.session.add(derivative1)
    db.session.flush()

    derivative2 = Derivative(
        attachment=attachment_instance,
        mime_type=attachment_instance.mime_type,
        width=1000,
        height=750,
        allow_crop=True)
    db.session.add(derivative2)

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.flush()


def test_derivative_ensure_storage_data(attachment_instance_with_data):
    """
    Should create storage data if it is needed, and no-op otherwise.
    """
    derivative = Derivative(
        attachment=attachment_instance_with_data,
        mime_type=attachment_instance_with_data.mime_type)

    derivative.set_storage_data_from_image = Mock()

    with patch(
            'windowbox.models.derivative.Derivative.has_storage_data',
            new_callable=PropertyMock) as mock_sd:
        mock_sd.return_value = True
        derivative.ensure_storage_data()
        derivative.set_storage_data_from_image.assert_not_called()

        mock_sd.return_value = False
        derivative.ensure_storage_data()
        derivative.set_storage_data_from_image.assert_called()

        # Belt-and-suspenders; verify it was called with the expected image
        [out_img], _ = derivative.set_storage_data_from_image.call_args
        out_pix = out_img.convert('RGB').load()
        assert out_img.size == (100, 76)
        assert out_pix[0, 0] == (255, 0, 0)
        assert out_pix[99, 0] == (0, 255, 0)
        assert out_pix[0, 75] == (0, 0, 255)
        assert out_pix[99, 75] == (0, 0, 0)


def test_derivative_to_image_transpose(attachment_instance_with_data):
    """
    Should rotate/flip images as required.
    """
    derivative = Derivative(
        attachment=attachment_instance_with_data,
        mime_type=attachment_instance_with_data.mime_type)

    # Make sure it doesn't raise on crap input
    derivative.attachment.orientation = None
    derivative.to_image()
    derivative.attachment.orientation = '1'
    derivative.to_image()
    derivative.attachment.orientation = 999
    derivative.to_image()

    # Orientation 1: No change relative to the original
    derivative.attachment.orientation = 1
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()
    assert out_img.size == (100, 76)
    assert out_pix[0, 0] == (255, 0, 0)
    assert out_pix[99, 0] == (0, 255, 0)
    assert out_pix[0, 75] == (0, 0, 255)
    assert out_pix[99, 75] == (0, 0, 0)

    # Orientation 2: Flip horizontal
    derivative.attachment.orientation = 2
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()
    assert out_img.size == (100, 76)
    assert out_pix[0, 0] == (0, 255, 0)
    assert out_pix[99, 0] == (255, 0, 0)
    assert out_pix[0, 75] == (0, 0, 0)
    assert out_pix[99, 75] == (0, 0, 255)

    # Orientation 3: Rotate 180 degrees
    derivative.attachment.orientation = 3
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()
    assert out_img.size == (100, 76)
    assert out_pix[0, 0] == (0, 0, 0)
    assert out_pix[99, 0] == (0, 0, 255)
    assert out_pix[0, 75] == (0, 255, 0)
    assert out_pix[99, 75] == (255, 0, 0)

    # Orientation 4: Flip vertical
    derivative.attachment.orientation = 4
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()
    assert out_img.size == (100, 76)
    assert out_pix[0, 0] == (0, 0, 255)
    assert out_pix[99, 0] == (0, 0, 0)
    assert out_pix[0, 75] == (255, 0, 0)
    assert out_pix[99, 75] == (0, 255, 0)

    # Orientation 5: Flip about "top-left to bottom-right" diagonal
    derivative.attachment.orientation = 5
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()
    assert out_img.size == (76, 100)
    assert out_pix[0, 0] == (255, 0, 0)
    assert out_pix[75, 0] == (0, 0, 255)
    assert out_pix[0, 99] == (0, 255, 0)
    assert out_pix[75, 99] == (0, 0, 0)

    # Orientation 6: Rotate 90 degrees clockwise
    derivative.attachment.orientation = 6
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()
    assert out_img.size == (76, 100)
    assert out_pix[0, 0] == (0, 0, 255)
    assert out_pix[75, 0] == (255, 0, 0)
    assert out_pix[0, 99] == (0, 0, 0)
    assert out_pix[75, 99] == (0, 255, 0)

    # Orientation 7: Flip about "bottom-left to top-right" diagonal
    derivative.attachment.orientation = 7
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()
    assert out_img.size == (76, 100)
    assert out_pix[0, 0] == (0, 0, 0)
    assert out_pix[75, 0] == (0, 255, 0)
    assert out_pix[0, 99] == (0, 0, 255)
    assert out_pix[75, 99] == (255, 0, 0)

    # Orientation 8: Rotate 90 degrees counterclockwise
    derivative.attachment.orientation = 8
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()
    assert out_img.size == (76, 100)
    assert out_pix[0, 0] == (0, 255, 0)
    assert out_pix[75, 0] == (0, 0, 0)
    assert out_pix[0, 99] == (255, 0, 0)
    assert out_pix[75, 99] == (0, 0, 255)


def test_derivative_to_image_constrained_crop(attachment_instance_with_data):
    """
    Should be able to force an image to any specified size by cropping.
    """

    # First try a short/fat image.
    derivative = Derivative(
        attachment=attachment_instance_with_data,
        mime_type=attachment_instance_with_data.mime_type,
        width=50,
        height=10,
        allow_crop=True)
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()

    assert out_img.size == (50, 10)
    assert out_pix[0, 0] == (255, 0, 0)
    assert out_pix[49, 0] == (0, 255, 0)
    assert out_pix[0, 9] == (0, 0, 255)
    assert out_pix[49, 9] == (0, 0, 0)

    # Same thing, but with a tall/skinny image
    derivative.width = 10
    derivative.height = 50
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()

    assert out_img.size == (10, 50)
    assert out_pix[0, 0] == (255, 0, 0)
    assert out_pix[9, 0] == (0, 255, 0)
    assert out_pix[0, 49] == (0, 0, 255)
    assert out_pix[9, 49] == (0, 0, 0)


def test_derivative_to_image_constrained_no_crop(attachment_instance_with_data):
    """
    Should be able to fit an image within the size by ignoring the longer side.
    """

    # First try a short/fat image.
    derivative = Derivative(
        attachment=attachment_instance_with_data,
        mime_type=attachment_instance_with_data.mime_type,
        width=50,
        height=10,
        allow_crop=False)
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()

    assert out_img.size == (13, 10)
    assert out_pix[0, 0] == (255, 0, 0)
    assert out_pix[12, 0] == (0, 255, 0)
    assert out_pix[0, 9] == (0, 0, 255)
    assert out_pix[12, 9] == (0, 0, 0)

    # Same thing, but with a tall/skinny image
    derivative.width = 10
    derivative.height = 50
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()

    assert out_img.size == (10, 8)
    assert out_pix[0, 0] == (255, 0, 0)
    assert out_pix[9, 0] == (0, 255, 0)
    assert out_pix[0, 7] == (0, 0, 255)
    assert out_pix[9, 7] == (0, 0, 0)


def test_derivative_to_image_width(attachment_instance_with_data):
    """
    Should be able to resize an image given only width.
    """
    derivative = Derivative(
        attachment=attachment_instance_with_data,
        mime_type=attachment_instance_with_data.mime_type,
        width=20,
        height=None,
        allow_crop=False)
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()

    assert out_img.size == (20, 15)
    assert out_pix[0, 0] == (255, 0, 0)
    assert out_pix[19, 0] == (0, 255, 0)
    assert out_pix[0, 14] == (0, 0, 255)
    assert out_pix[19, 14] == (0, 0, 0)


def test_derivative_to_image_height(attachment_instance_with_data):
    """
    Should be able to resize an image given only height.
    """
    derivative = Derivative(
        attachment=attachment_instance_with_data,
        mime_type=attachment_instance_with_data.mime_type,
        width=None,
        height=30,
        allow_crop=False)
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()

    assert out_img.size == (39, 30)
    assert out_pix[0, 0] == (255, 0, 0)
    assert out_pix[29, 0] == (0, 255, 0)
    assert out_pix[0, 22] == (0, 0, 255)
    assert out_pix[29, 22] == (0, 0, 0)


def test_derivative_to_image_full(attachment_instance_with_data):
    """
    Should be able to pass the original image size through.
    """
    derivative = Derivative(
        attachment=attachment_instance_with_data,
        mime_type=attachment_instance_with_data.mime_type,
        width=None,
        height=None,
        allow_crop=False)
    out_img = derivative.to_image()
    out_pix = out_img.convert('RGB').load()

    assert out_img.size == (100, 76)
    assert out_pix[0, 0] == (255, 0, 0)
    assert out_pix[99, 0] == (0, 255, 0)
    assert out_pix[0, 75] == (0, 0, 255)
    assert out_pix[99, 75] == (0, 0, 0)
