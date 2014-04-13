from windowbox.models.post import PostManager
from windowbox.views.index import IndexView
from windowbox.views.page import PageView


class IndexHandler():
    @classmethod
    def get(cls, until_id=None, as_json=False):
        render = cls.render_json if as_json else cls.render_html
        posts = PostManager.get_all(until_id=until_id)

        return render(posts)

    @staticmethod
    def render_html(posts):
        body_html = IndexView(items=posts).render_html()

        return PageView(title=None, body=body_html).render_html()

    @staticmethod
    def render_json(posts):
        return 'TODO not implemented'
