from flask import abort
from windowbox.models.post import PostManager
from windowbox.views.index import IndexView
from windowbox.views.page import PageView


class IndexHandler():
    page_limit = 9

    @classmethod
    def get(cls, until_id=None, as_json=False):
        render = cls._render_json if as_json else cls._render_html
        posts, has_next = PostManager.get_all(until_id=until_id, limit=cls.page_limit)

        return render(posts, has_next)

    @staticmethod
    def _render_html(posts, has_next):
        try:
            body_html = IndexView(items=posts, has_next=has_next).render_html()

            return PageView(title=None, body=body_html).render_html()
        except IndexError:
            abort(404)

    @staticmethod
    def _render_json(posts, has_next):
        return 'TODO not implemented'
