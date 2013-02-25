from re import match
from flask import Flask, render_template, make_response, abort
from jinja2.exceptions import UndefinedError

app = Flask(__name__)
app.config.from_object('windowboxconfig')

from windowbox.models.post import Post


@app.errorhandler(404)
def page_not_found(error):
    return 'You screwed up!', 404


@app.route('/')
def index():
    posts = Post.get_all()

    return render_template('index.html', posts=posts)


@app.route('/post/<int:post_id>')
def single_post(post_id):
    try:
        post = Post.get_by_id(post_id)
        previous, next = post.get_adjacent()

        return render_template('single_post.html', post=post, previous=previous, next=next)
    except (AttributeError, UndefinedError):
        abort(404)


@app.route('/image/<int:post_id>', defaults={'size': ''})
@app.route('/image/<int:post_id>/<size>')
def image_data(post_id, size):
    matches = match('(\d*)x(\d*)', size)
    w, h = matches.groups() if matches else (None, None)

    try:
        post = Post.get_by_id(post_id)
        image = post.image

        response = make_response(image.get_resized_data(width=w, height=h))
        response.headers['Content-Type'] = image.mime_type
        return response
    except (AttributeError, UndefinedError):
        abort(404)
