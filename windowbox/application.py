from flask import Flask
from windowbox.database import sess as db_session
from windowbox.handlers.index import IndexHandler
from windowbox.handlers.single_post import SinglePostHandler
from windowbox.handlers.image_data import ImageDataHandler

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(error):
    return 'You screwed up!', 404


@app.route('/')
def index():
    return IndexHandler().get()


@app.route('/post/<int:post_id>')
def single_post(post_id):
    return SinglePostHandler().get(post_id)


@app.route('/image/<int:post_id>', defaults={'size': None})
@app.route('/image/<int:post_id>/<size>')
def image_data(post_id, size):
    return ImageDataHandler().get(post_id, size)


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
