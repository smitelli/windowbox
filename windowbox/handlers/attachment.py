from flask import make_response, abort
from windowbox.application import app
from windowbox.models.attachment import AttachmentManager


class AttachmentDerivativeHandler():
    @staticmethod
    def get(attachment_id=None, dimensions='', allow_crop=True):
        if dimensions in app.config['ALLOWED_DIMENSIONS']:
            width, height = AttachmentManager.decode_dimensions(dimensions)
        else:
            width = height = None

        try:
            attachment = AttachmentManager.get_by_id(attachment_id)
            derivative = attachment.get_derivative(width, height, allow_crop=allow_crop)

            response = make_response(derivative.get_data())
            response.headers['Content-Type'] = derivative.mime_type

            return response
        except (AttributeError):
            abort(404)
