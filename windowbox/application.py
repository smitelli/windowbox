from flask import Flask
from windowbox.database import session as db_session
from windowbox.handlers.index import IndexHandler
from windowbox.handlers.post import PostHandler
from windowbox.handlers.attachment import AttachmentHandler

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(error):
    return 'You screwed up!', 404


@app.route('/')
def get_index():
    return IndexHandler.get()


@app.route('/post/<int:post_id>')
def get_post(post_id):
    return PostHandler.get(post_id)


@app.route('/attachment/<int:attachment_id>')
@app.route('/attachment/<int:attachment_id>/<dimensions>')
def get_attachment_derivative(attachment_id, dimensions=''):
    return AttachmentHandler.get(attachment_id, dimensions)


@app.teardown_request
def shutdown_session(exception=None):
    db_session.close()
