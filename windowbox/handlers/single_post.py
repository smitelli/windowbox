from flask import render_template, abort
from jinja2.exceptions import UndefinedError
from windowbox.models.post import Post


class SinglePostHandler():
    def get(self, post_id=None):
        try:
            post = Post.get_by_id(post_id)
            previous, next = post.get_adjacent()

            return render_template('single_post.html', post=post, previous=previous, next=next)
        except (AttributeError, UndefinedError):
            abort(404)
