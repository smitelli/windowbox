from flask import render_template
from windowbox.models.post import Post


class IndexHandler():
    def get(self):
        posts = Post.get_all()

        return render_template('index.html', posts=posts)
