from flask import Flask, make_response
from database import db_session
from models import Post

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/post/<int:post_id>')
def single_post(post_id):
    post = Post.query.filter(Post.id == post_id).first()

    return post.message + '<br><img src="/image/' + str(post.image_id) + '">'


@app.route('/image/<int:post_id>')
def image_data(post_id):
    post = Post.query.filter(Post.id == post_id).first()
    image = post.get_image()

    response = make_response(image.data)
    response.headers['Content-Type'] = image.mime_type
    return response


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    app.run(debug=True)
