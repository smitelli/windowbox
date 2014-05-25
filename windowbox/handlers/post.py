from flask import abort
from jinja2.exceptions import UndefinedError
from windowbox.models.metadata import Metadata
from windowbox.models.post import PostManager
from windowbox.views.page import PageView
from windowbox.views.single import SingleView


class PostHandler():
    @classmethod
    def get(cls, post_id=None, as_json=False):
        try:
            render = cls._render_json if as_json else cls._render_html

            post = PostManager.get_by_id(post_id)
            attachment = post.get_attachment()
            metadata = Metadata(attachment.attributes)
            previous, next = PostManager.get_adjacent_by_id(post_id)

            return render(post, attachment, metadata, previous, next)
        except (AttributeError, UndefinedError):
            abort(404)

    @staticmethod
    def _render_html(post, attachment, metadata, previous, next):
        body_html = SingleView(
            item=post, attachment=attachment, metadata=metadata,
            prev_item=previous, next_item=next).render_html()

        return PageView(title=post.message, body=body_html).render_html()

    @staticmethod
    def _render_json(post, attachment, metadata, previous, next):
        return 'TODO not implemented either'
