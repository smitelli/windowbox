from flask import Flask, render_template, make_response, abort
from re import match
from database import db_session
from models import Post

app = Flask(__name__)


@app.route('/')
def index():
    posts = Post.get_all()

    return render_template('index.html', posts=posts)


@app.route('/post/<int:post_id>')
def single_post(post_id):
    post = Post.get_by_id(post_id)

    if post is None:
        abort(404)

    return render_template('single_post.html', post=post)


@app.route('/image/<int:post_id>', defaults={'size': ''})
@app.route('/image/<int:post_id>/<size>')
def image_data(post_id, size):
    post = Post.get_by_id(post_id)

    if post is None:
        abort(404)

    image = post.get_image()

    matches = match('(\d*)x(\d*)', size)
    w, h = matches.groups() if matches else (None, None)

    response = make_response(image.get_resized_data(width=w, height=h))
    response.headers['Content-Type'] = image.mime_type
    return response


@app.errorhandler(404)
def page_not_found(error):
    return 'You screwed up!', 404


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
