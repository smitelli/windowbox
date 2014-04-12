from flask import render_template, abort
from jinja2.exceptions import UndefinedError
from windowbox.models.post import PostManager


class PostHandler():
    @classmethod
    def get(cls, post_id=None, as_json=False):
        try:
            render = cls.render_json if as_json else cls.render_html
            post = PostManager.get_by_id(post_id)
            previous, next = PostManager.get_adjacent_by_id(post_id)

            return render(post, previous, next)
        except (AttributeError, UndefinedError):
            abort(404)

    @staticmethod
    def render_html(post, previous, next):
        template_vars = {
            'post': post,
            'previous': previous,
            'next': next}

        return render_template('single_post.html', **template_vars)

    @staticmethod
    def render_json(post, previous, next):
        return 'TODO not implemented either'
