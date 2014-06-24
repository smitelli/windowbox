from __future__ import absolute_import
from flask import current_app, make_response
from windowbox.handlers import get_or_404
from windowbox.models.attachment import AttachmentManager


class AttachmentDerivativeHandler(object):
    @staticmethod
    def get(attachment_id=None, dimensions='', allow_crop=True):
        if dimensions in current_app.config['ALLOWED_DIMENSIONS']:
            width, height = AttachmentManager.decode_dimensions(dimensions)
        else:
            current_app.logger.debug('`%s` is not in ALLOWED_DIMENSIONS', dimensions)
            width = height = None

        attachment = get_or_404(AttachmentManager.get_by_id, attachment_id)
        derivative = attachment.get_derivative(width, height, allow_crop=allow_crop)

        response = make_response(derivative.get_data())
        response.headers['Content-Type'] = derivative.mime_type

        return response
