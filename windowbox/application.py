from flask import Flask
from windowbox.database import session as db_session
from windowbox.handlers.index import IndexHandler
from windowbox.handlers.post import PostHandler
from windowbox.handlers.image import ImageHandler

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(error):
    return 'You screwed up!', 404


@app.route('/')
def get_index():
    return IndexHandler().get()


@app.route('/post/<int:post_id>')
def get_post(post_id):
    return PostHandler().get(post_id)


@app.route('/image/<int:post_id>', defaults={'size': None})
@app.route('/image/<int:post_id>/<size>')
def get_image(post_id, size):
    return ImageHandler().get(post_id, size)


@app.teardown_request
def shutdown_session(exception=None):
    db_session.close()
