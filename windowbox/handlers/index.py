from flask import render_template
from windowbox.models.post import PostManager


class IndexHandler():
    def get(self):
        posts = PostManager().get_all()

        template_vars = {
            'posts': posts}

        return render_template('index.html', **template_vars)
