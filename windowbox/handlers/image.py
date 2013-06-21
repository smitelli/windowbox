from flask import make_response, abort
from jinja2.exceptions import UndefinedError
from windowbox.models.image import ImageFactory


class ImageHandler():
    def get(self, post_id=None, size=None):
        image = ImageFactory().get_derivative(post_id=post_id, size=size)

        response = make_response(image.get_data())
        response.headers['Content-Type'] = image.mime_type

        return response
