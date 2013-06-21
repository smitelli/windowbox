from flask import render_template, abort
from jinja2.exceptions import UndefinedError
from windowbox.models.post import PostFactory


class PostHandler():
    def get(self, post_id=None):
        try:
            post = PostFactory().get_by_id(post_id)
            previous, next = PostFactory().get_adjacent_by_id(post_id)

            template_vars = {
                'post': post,
                'previous': previous,
                'next': next}

            return render_template('single_post.html', **template_vars)
        except (AttributeError, UndefinedError):
            abort(404)
