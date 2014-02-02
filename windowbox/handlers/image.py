import re
from flask import make_response, abort
from windowbox.models.image import ImageManager


class ImageHandler():
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

            image = ImageManager().get_image_by_post_id(post_id=post_id)
            deriv = image.get_derivative(width, height)

            response = make_response(deriv.get_data())
            response.headers['Content-Type'] = deriv.mime_type

            return response
        except (AttributeError):
            abort(404)
