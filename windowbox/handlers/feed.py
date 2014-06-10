from __future__ import absolute_import
from windowbox.models.post import PostManager
from windowbox.views.index import IndexView


class FeedHandler():
    item_limit = 30

    @classmethod
    def get_rss2(cls):
        posts, has_next = PostManager.get_all(limit=cls.item_limit)

        response = IndexView(items=posts, has_next=has_next).render_rss2()

        return response

    @classmethod
    def get_atom(cls):
        posts, has_next = PostManager.get_all(limit=cls.item_limit)

        response = IndexView(items=posts, has_next=has_next).render_atom()

        return response
