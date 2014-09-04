from __future__ import absolute_import
from windowbox.models.post import PostManager
from windowbox.views.index import IndexView


class FeedHandler(object):
    ITEM_LIMIT = 30

    @classmethod
    def get_rss2(cls):
        posts, has_next = PostManager.get_all(limit=cls.ITEM_LIMIT)

        return IndexView(items=posts, has_next=has_next, mode=IndexView.MODE_SINCE).render_rss2()

    @classmethod
    def get_atom(cls):
        posts, has_next = PostManager.get_all(limit=cls.ITEM_LIMIT)

        return IndexView(items=posts, has_next=has_next, mode=IndexView.MODE_SINCE).render_atom()

    @classmethod
    def get_sitemap(cls):
        posts, has_next = PostManager.get_all()

        return IndexView(items=posts, has_next=has_next, mode=IndexView.MODE_SINCE).render_sitemap()
