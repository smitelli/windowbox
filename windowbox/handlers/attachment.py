import re
from flask import make_response, abort
from windowbox.models.attachment import AttachmentManager


class AttachmentHandler():
    def get(self, post_id=None, dimensions=''):
        try:
            matches = re.match('(?P<width>\d*)x(?P<height>\d*)', dimensions)

            if matches:
                def str_to_int(value):
                    try:
                        return int(value)
                    except ValueError:
                        return None

                width = str_to_int(matches.group('width'))
                height = str_to_int(matches.group('height'))
            else:
                width = height = None

            attachment = AttachmentManager().get_attachment_by_post_id(post_id=post_id)
            derivative = attachment.get_derivative(width, height)

            response = make_response(derivative.get_data())
            response.headers['Content-Type'] = derivative.mime_type

            return response
        except (AttributeError):
            abort(404)
