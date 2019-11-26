"""
Attachment controller.

Attributes:
    DIMENSIONS_EXTRACTOR: Compiled regex pattern to match and extract components
        from Derivative URLs.
    FULL_EXTRACTOR: Compiled regex pattern to match "original size" URLs.
    logger: Logger instance scoped to the current module name.
"""

import logging
import re
import sqlalchemy.orm.exc
from flask import current_app
from windowbox.controllers import BaseController
from windowbox.database import db
from windowbox.models.attachment import Attachment, Dimensions
from windowbox.models.derivative import Derivative

# All defined crop flags
_cf = f'{Attachment.CROP_FLAG_ALLOW}{Attachment.CROP_FLAG_DISALLOW}'

DIMENSIONS_EXTRACTOR = re.compile(
    rf'^(?P<width>\d*)(?P<crop_flag>[{_cf}])(?P<height>\d*)(?P<extension>\..+)?$')
FULL_EXTRACTOR = re.compile(r'^full(?P<extension>\..+)?$')

logger = logging.getLogger(__name__)


class AttachmentController(BaseController):
    """
    Attachment controller.

    Responsible for creation and lookup of Attachment models and the Derivative
    models that can be built from them.

    NOTE: Any time a file extension is provided in a URL, it's mainly for show.
    None of the controller methods actually parse the extension's value or
    change their behavior based on its presence. The ONLY REASON extensions are
    used at all is to serve as a hint to other online services (*cough* Slack)
    that the URL refers to an image and should be embedded as such.
    """

    @staticmethod
    def message_to_data(message):
        """
        Build and yield Attachment data parts from an IMAP message.

        Args:
            message: An message instance as returned by the IMAP client.

        Yields:
            Tuple of (mime_type, part_data) for each usable message part
            encountered in the provided message.
        """
        known_types = set(Attachment.KNOWN_EXTENSIONS)

        for mime_type in sorted(known_types.intersection(message.part_types)):
            for part_data in message.yield_parts(mime_type):
                yield mime_type, part_data

    @classmethod
    def get_by_id(cls, attachment_id):
        """
        Return one Attachment model from an ID.

        Args:
            attachment_id: The primary key of an Attachment to get.

        Returns:
            Attachment instance matching the provided argument.

        Raises:
            NoResultFound: The provided ID didn't match any known Attachments.
        """
        try:
            return Attachment.query.filter_by(id=attachment_id).one()
        except sqlalchemy.orm.exc.NoResultFound as exc:
            raise cls.NoResultFound from exc

    @staticmethod
    def decode_dimensions(dim_str):
        """
        Decode a dimensions string (like from a URL) into a Dimensions tuple.

        Args:
            dim_str: String in the format "100x100.jpg" or "full.jpg"

        Returns:
            Dimensions namedtuple if the format can be matched, or None if the
            format was invalid.
        """
        if FULL_EXTRACTOR.match(dim_str) is not None:
            return Dimensions(width=None, height=None, allow_crop=False)

        match = DIMENSIONS_EXTRACTOR.match(dim_str)
        if match is None:
            logger.debug(f'Could not extract dimensions from {dim_str}')
            return None

        width = match.group('width')
        height = match.group('height')
        allow_crop = (match.group('crop_flag') == Attachment.CROP_FLAG_ALLOW)

        # Need at least one of (width, height) to continue with the request
        if not any([width, height]):
            logger.debug(f'Could not find width or height in {dim_str}')
            return None

        return Dimensions(
            width=int(width) if width else None,
            height=int(height) if height else None,
            allow_crop=allow_crop)

    @classmethod
    def get_attachment_derivative(cls, *, attachment_id, dimensions):
        """
        Given an Attachment ID and a dimensions string, return a Derivative.

        If a Derivative already exists, it is returned directly. Otherwise a new
        Derivative is created from the Attachment. If the final Derivative does
        not have storage data, it is transparently generated before returning.

        Args:
            attachment_id: The primary key of an Attachment to get.
            dimensions: String specifying the size and crop characteristics of
                the Derivative to return.

        Returns:
            One Derivative instance matching the provided arguments.

        Raises:
            NoResultFound: The provided ID didn't match any known Attachments,
                or the dimensions were not able to be decoded.
        """
        attachment = cls.get_by_id(attachment_id)

        dim_tuple = cls.decode_dimensions(dimensions)
        if dim_tuple is None:
            raise cls.NoResultFound

        # To avoid denial of service, refuse to serve arbitrary client-provided
        # sizes and only allow ones we've explicitly defined.
        if dim_tuple not in Attachment.CANNED_DIMENSIONS_MAP.values():
            raise cls.NoResultFound

        return cls.make_or_get_derivative(attachment=attachment, dim_tuple=dim_tuple)

    @staticmethod
    def make_or_get_derivative(*, attachment, dim_tuple):
        """
        Build or retrieve a Derivative, given an Attachment and dimensions.

        This method abstracts away the differences between fresh and existing
        Derivatives, and present/missing storage data.

        NOTE: This method relies on there being a properly configured Flask app
        since the Attachment/Derivative paths from the app config need to be
        known here. It was decided not to pass these paths as arguments due to
        the unreasonable burden that would place on the calling code.

        Args:
            attachment: Instance of Attachment that owns and feeds the returned
                Derivative.
            dim_tuple: Dimensions namedtuple containing the desired dimensions
                of the Derivative to make or get.

        Returns:
            Instance of Derivative, fully committed to the database, with
            storage data already built.
        """
        attachments_path = current_app.attachments_path
        derivatives_path = current_app.derivatives_path

        try:
            derivative = Derivative.query.filter_by(
                attachment=attachment,
                width=dim_tuple.width,
                height=dim_tuple.height,
                allow_crop=dim_tuple.allow_crop).one()
        except sqlalchemy.orm.exc.NoResultFound:
            logger.debug(
                f'Creating {dim_tuple.width}x{dim_tuple.height},{dim_tuple.allow_crop} '
                f'Derivative from Attachment ID {attachment.id}')

            derivative = attachment.new_derivative(
                width=dim_tuple.width,
                height=dim_tuple.height,
                allow_crop=dim_tuple.allow_crop)
            db.session.add(derivative)
            db.session.commit()

        attachment.base_path = attachments_path
        derivative.base_path = derivatives_path

        derivative.ensure_storage_data()

        return derivative
