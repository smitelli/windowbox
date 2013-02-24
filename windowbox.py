from flask import Flask, render_template, make_response
from database import db_session
from models import Post

app = Flask(__name__)


@app.route('/')
def index():
    posts = Post.query.order_by(Post.id).all()

    return render_template('index.html', posts=posts)


@app.route('/post/<int:post_id>')
def single_post(post_id):
    post = Post.query.filter(Post.id == post_id).first()

    return render_template('single_post.html', post=post)


@app.route('/image/<int:post_id>')
def image_data(post_id):
    image = Post.query.filter(Post.id == post_id).first().get_image()

    response = make_response(image.data)
    response.headers['Content-Type'] = image.mime_type
    return response


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    app.run(debug=True)
