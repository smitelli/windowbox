from flask import make_response, abort
from windowbox.models.attachment import AttachmentManager


class AttachmentHandler():
    @staticmethod
    def get(attachment_id=None, dimensions=''):
        try:
            attachment = AttachmentManager.get_by_id(attachment_id=attachment_id)
            width, height = AttachmentManager.decode_dimensions(dimensions)

            derivative = attachment.get_derivative(width, height)

            response = make_response(derivative.get_data())
            response.headers['Content-Type'] = derivative.mime_type

            return response
        except (AttributeError):
            abort(404)
