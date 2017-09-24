from __future__ import absolute_import
from flask import abort, jsonify
from windowbox.handlers import get_or_404
from windowbox.models.post import PostManager
from windowbox.views.index import IndexView
from windowbox.views.page import PageView


class IndexHandler(object):
    ITEM_LIMIT = 9

    @classmethod
    def get(cls, since_id=None, until_id=None, as_json=False):
        if since_id is not None and until_id is not None:
            abort(400)

        render = cls._render_json if as_json else cls._render_html
        mode = IndexView.MODE_SINCE if since_id is not None else IndexView.MODE_UNTIL

        posts, has_next = get_or_404(PostManager.get_all, since_id=since_id, until_id=until_id, limit=cls.ITEM_LIMIT)

        return render(posts, has_next, mode)

    @staticmethod
    def _render_html(posts, has_next, mode):
        body_html = IndexView(items=posts, has_next=has_next, mode=mode).render_html()

        return PageView(title=None, body=body_html).render_html()

    @staticmethod
    def _render_json(posts, has_next, mode):
        post_list = [p.to_dict(lookup_children=True) for p in posts]

        return jsonify(posts=post_list, has_next=has_next)
