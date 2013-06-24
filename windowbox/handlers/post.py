from flask import render_template, abort
from jinja2.exceptions import UndefinedError
from windowbox.models.post import PostFactory


class PostHandler():
    def get(self, post_id=None):
        try:
            post = PostFactory().get_by_id(post_id)
            previous, next = PostFactory().get_adjacent_by_id(post_id)

            # TODO Temporary!
            from pprint import pprint
            from windowbox.models.image import ImageFactory
            pprint(ImageFactory().get_original_by_id(post_id=post_id).exif_data)

            template_vars = {
                'post': post,
                'previous': previous,
                'next': next}

            return render_template('single_post.html', **template_vars)
        except (AttributeError, UndefinedError):
            abort(404)
