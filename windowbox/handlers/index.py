from __future__ import absolute_import
from flask import jsonify
from windowbox.handlers import get_or_404
from windowbox.models.post import PostManager
from windowbox.views.index import IndexView
from windowbox.views.page import PageView


class IndexHandler(object):
    ITEM_LIMIT = 9

    @classmethod
    def get(cls, until_id=None, as_json=False):
        render = cls._render_json if as_json else cls._render_html

        posts, has_next = get_or_404(PostManager.get_all, until_id=until_id, limit=cls.ITEM_LIMIT)

        return render(posts, has_next)

    @staticmethod
    def _render_html(posts, has_next):
        body_html = IndexView(items=posts, has_next=has_next).render_html()

        return PageView(title=None, body=body_html).render_html()

    @staticmethod
    def _render_json(posts, has_next):
        return jsonify(TODO='not implemented')
