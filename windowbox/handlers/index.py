from windowbox.models.post import PostManager
from windowbox.views.index import IndexView
from windowbox.views.page import PageView

PER_PAGE = 10


class IndexHandler():
    @classmethod
    def get(cls, until_id=None, as_json=False):
        render = cls.render_json if as_json else cls.render_html
        posts, has_next = PostManager.get_all(until_id=until_id, limit=PER_PAGE)

        return render(posts, has_next)

    @staticmethod
    def render_html(posts, has_next):
        body_html = IndexView(items=posts, has_next=has_next).render_html()

        return PageView(title=None, body=body_html).render_html()

    @staticmethod
    def render_json(posts, has_next):
        return 'TODO not implemented'
