from flask import abort
from jinja2.exceptions import UndefinedError
from windowbox.models.post import PostManager
from windowbox.views.page import PageView
from windowbox.views.single import SingleView


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
        body_html = SingleView(item=post, prev_item=previous, next_item=next).render_html()

        return PageView(title=post.message, body=body_html).render_html()

    @staticmethod
    def render_json(post, previous, next):
        return 'TODO not implemented either'
