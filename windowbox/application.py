from flask import Flask, request
from windowbox.database import session as db_session
from windowbox.handlers.index import IndexHandler
from windowbox.handlers.post import PostHandler
from windowbox.handlers.attachment import AttachmentHandler
from windowbox.handlers.feed import FeedHandler

app = Flask(__name__)


def request_wants_json():
    json_score = request.accept_mimetypes['application/json']
    html_score = request.accept_mimetypes['text/html']
    return json_score > html_score


@app.errorhandler(404)
def page_not_found(error):
    return 'You screwed up!', 404


@app.route('/')
def get_index():
    until_id = request.args.get('until')
    as_json = request_wants_json()
    return IndexHandler.get(until_id=until_id, as_json=as_json)


@app.route('/post/<int:post_id>')
def get_post(post_id):
    as_json = request_wants_json()
    return PostHandler.get(post_id, as_json=as_json)


@app.route('/attachment/<int:attachment_id>')
@app.route('/attachment/<int:attachment_id>/<dimensions>')
def get_attachment_derivative(attachment_id, dimensions=''):
    return AttachmentHandler.get(attachment_id, dimensions)


@app.route('/rss')
def get_rss2():
    return FeedHandler.get_rss2()


@app.route('/atom')
def get_atom():
    return FeedHandler.get_atom()


@app.teardown_request
def shutdown_session(exception=None):
    db_session.close()
