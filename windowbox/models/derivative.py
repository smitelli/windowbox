"""
Derivative model.

Attributes:
    logger: Logger instance scoped to the current module name.
"""

import logging
from PIL.Image import Resampling, Transform, Transpose
from windowbox.database import db
from windowbox.models import FilesystemMixin
from windowbox.models.attachment import Attachment

logger = logging.getLogger(__name__)


def exif_transpose(*, image, orientation):
    """
    Rotate and/or flip an Image based on an EXIF orientation code.

    The purpose of this function is to cancel out the rotation of the camera at
    the moment a picture was taken and produce an image that looks correct
    without any additional metadata or filtering.

    Diagram (from http://sylvana.net/jpegcrop/exif_orientation.html):

          1      2      3      4        5          6          7          8
        ------ ------ ------ ------ ---------- ---------- ---------- ----------
        888888 888888     88 88     8888888888 88                 88 8888888888
        88         88     88 88     88  88     88  88         88  88     88  88
        8888     8888   8888 8888   88         8888888888 8888888888         88
        88         88     88 88
        88         88 888888 888888

    Args:
        image: Instance of a PIL Image.
        orientation: Numeric code read from the EXIF headers.

    Returns:
        PIL Image, correctly oriented.
    """
    methods = {
        '2': Transpose.FLIP_LEFT_RIGHT,  # flip horizontally
        '3': Transpose.ROTATE_180,  # rotate 180 degrees
        '4': Transpose.FLIP_TOP_BOTTOM,  # flip vertically
        '5': Transpose.TRANSPOSE,  # flip about "top-left to bottom-right" diagonal
        '6': Transpose.ROTATE_270,  # rotate 90 degrees clockwise
        '7': Transpose.TRANSVERSE,  # flip about "bottom-left to top-right" diagonal
        '8': Transpose.ROTATE_90  # rotate 90 degrees counterclockwise
    }

    method = methods.get(str(orientation))
    if method is not None:
        image = image.transpose(method)

    return image


def intround(value):
    """
    Round and cast a value to int.

    For a scalar value, rounds then converts directly to int. For a tuple,
    performs these steps for each element and returns a new tuple.

    Args:
        value: A numeric scalar value, or a tuple of same.

    Returns:
        Same as input type, with all numbers rounded to int.
    """
    if isinstance(value, tuple):
        return tuple(intround(v) for v in value)
    else:
        return int(round(value))


class Derivative(db.Model, FilesystemMixin):
    """
    Derivative model.

    A Derivative is an altered copy of an Attachment, generally with a different
    size, crop, or image format.

    Attributes:
        MIME_TYPE_LENGTH: The maximum size of the mime_type column.
    """

    MIME_TYPE_LENGTH = Attachment.MIME_TYPE_LENGTH

    __table_args__ = (
        db.Index(
            'attachment_id_dimensions', 'attachment_id', 'width', 'height',
            'allow_crop', unique=True),
    )
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    attachment_id = db.Column(
        db.Integer, db.ForeignKey('attachment.id', ondelete='CASCADE'),
        nullable=False, index=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    allow_crop = db.Column(db.Boolean, nullable=False)
    mime_type = db.Column(db.Unicode(length=MIME_TYPE_LENGTH), nullable=False)

    attachment = db.relationship(
        Attachment, backref=db.backref('derivatives', cascade='all, delete-orphan'))

    def ensure_storage_data(self):
        """
        Build the storage path data if it doesn't already exist.

        If the data already exists, this method is a no-op.
        """
        if not self.has_storage_data:
            logger.debug(f'Generating storage data for Derivative ID {self.id}')

            image = self.to_image()
            self.set_storage_data_from_image(image)

    def to_image(self):
        """
        Build a fresh image object based on the current model state.

        Reads the storage path data as an image, rotates/flips it based on the
        embedded EXIF data (if present), then resizes the image based on the
        `width`, `height`, and `allow_crop` model attributes.

        Returns:
            New PIL Image object containing appropriate image data.
        """
        image = self.attachment.get_storage_data_as_image()

        # Fix camera orientation if needed
        image = exif_transpose(image=image, orientation=self.attachment.orientation)

        # `old` is the current size, `new` is the size to build
        old_w, old_h = image.size
        new_w, new_h = self.width, self.height

        if (new_w is not None) and (new_h is not None):
            # `scale` is the ratio of new to old (< 1.0 indicates reduction)
            scale_w = new_w / old_w
            scale_h = new_h / old_h

            if self.allow_crop:
                # Cropping means potentially losing picture area. Pick the
                # larger scale ratio to ensure the output is filled all around.
                scale = max(scale_w, scale_h)

                # Get the size of the source area using the `old` scale.
                source_w = new_w / scale
                source_h = new_h / scale

                # Determine how much to cut off the left/top edges to make the
                # source fit into the destination's shape. One of these should
                # always end up being zero!
                cut_l = (old_w - source_w) / 2
                cut_t = (old_h - source_h) / 2

                image = image.transform(
                    size=intround((source_w, source_h)), method=Transform.EXTENT,
                    data=intround((
                        cut_l, cut_t,
                        (source_w + cut_l), (source_h + cut_t))))
                new_size = new_w, new_h

            else:
                # No crop is desired, so one of the `new` dimensions is going to
                # need to be discarded. Keep the smaller scale ratio to fit the
                # entire output within the constraints, and reduce the other
                # dimension to keep everything proportional.
                scale = min(scale_w, scale_h)
                new_size = (old_w * scale), (old_h * scale)

        elif (new_w is not None) and (new_h is None):
            # Only care about width; height follows automatically.
            scale = new_w / old_w
            new_size = new_w, (old_h * scale)

        elif (new_w is None) and (new_h is not None):
            # Only care about height; width follows automatically.
            scale = new_h / old_h
            new_size = (old_w * scale), new_h

        else:
            # Most likely a full-size Derivative. Keep the existing dimensions.
            new_size = image.size

        return image.resize(size=intround(new_size), resample=Resampling.LANCZOS)
