from flask import make_response, abort
from windowbox.models.image import ImageFactory


class ImageHandler():
    def get(self, post_id=None, size=None):
        try:
            image = ImageFactory().get_derivative(post_id=post_id, size=size)

            response = make_response(image.get_data())
            response.headers['Content-Type'] = image.mime_type

            return response
        except (AttributeError):
            abort(404)
