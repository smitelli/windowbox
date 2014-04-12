from flask import render_template
from windowbox.models.post import PostManager


class IndexHandler():
    @classmethod
    def get(cls, until_id=None, as_json=False):
        render = cls.render_json if as_json else cls.render_html
        posts = PostManager.get_all(until_id=until_id)

        return render(posts)

    @staticmethod
    def render_html(posts):
        template_vars = {
            'posts': posts}

        return render_template('index.html', **template_vars)

    @staticmethod
    def render_json(posts):
        return 'TODO not implemented'
