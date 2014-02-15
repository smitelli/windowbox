from flask import render_template, abort
from jinja2.exceptions import UndefinedError
from windowbox.models.post import PostManager


class PostHandler():
    @staticmethod
    def get(post_id=None):
        try:
            post = PostManager.get_by_id(post_id)
            previous, next = PostManager.get_adjacent_by_id(post_id)

            template_vars = {
                'post': post,
                'previous': previous,
                'next': next}

            return render_template('single_post.html', **template_vars)
        except (AttributeError, UndefinedError):
            abort(404)
