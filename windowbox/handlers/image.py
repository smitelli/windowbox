from re import match
from flask import make_response, abort
from jinja2.exceptions import UndefinedError
from windowbox.models.post import PostFactory
from windowbox.models.imagedata import ImageDataFactory


class ImageHandler():
    def get(self, post_id=None, size=None):
        matches = match('(\d*)x(\d*)', size or '')
        w, h = matches.groups() if matches else (None, None)

        try:
            post = PostFactory().get_by_id(post_id)
            image = ImageDataFactory().get_by_id(post.post_id)

            response = make_response(image.get_resize(width=w, height=h))
            response.headers['Content-Type'] = image.mime_type
            return response
        except (AttributeError, UndefinedError):
            abort(404)
