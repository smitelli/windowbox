from re import match
from flask import make_response, abort
from jinja2.exceptions import UndefinedError
from windowbox.models.post import Post


class ImageHandler():
    def get(self, post_id=None, size=None):
        matches = match('(\d*)x(\d*)', size or '')
        w, h = matches.groups() if matches else (None, None)

        try:
            post = Post.get_by_id(post_id)
            image = post.image

            #TODO
            image.get_exif_data()

            response = make_response(image.get_resized_data(width=w, height=h))
            response.headers['Content-Type'] = image.mime_type
            return response
        except (AttributeError, UndefinedError):
            abort(404)
