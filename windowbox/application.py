from flask import Flask, request
from windowbox.database import session as db_session
from windowbox.handlers.attachment import AttachmentDerivativeHandler
from windowbox.handlers.error import ErrorHandler
from windowbox.handlers.feed import FeedHandler
from windowbox.handlers.index import IndexHandler
from windowbox.handlers.post import PostHandler

app = Flask(__name__)


def request_wants_json():
    json_score = request.accept_mimetypes['application/json']
    html_score = request.accept_mimetypes['text/html']
    return json_score > html_score


@app.errorhandler(404)
def page_not_found(error):
    return ErrorHandler.get(error, as_json=request_wants_json())


@app.route('/')
def get_index():
    until_id = request.args.get('until')
    return IndexHandler.get(until_id=until_id, as_json=request_wants_json())


@app.route('/post/<int:post_id>')
def get_post(post_id):
    return PostHandler.get(post_id, as_json=request_wants_json())


@app.route('/attachment/<int:attachment_id>')
@app.route('/attachment/<int:attachment_id>/<dimensions>')
def get_attachment_derivative(attachment_id, dimensions=''):
    allow_crop = False if request.args.get('crop') == 'false' else True
    return AttachmentDerivativeHandler.get(attachment_id, dimensions=dimensions, allow_crop=allow_crop)


@app.route('/rss.xml')
def get_rss2():
    return FeedHandler.get_rss2()


@app.route('/atom.xml')
def get_atom():
    return FeedHandler.get_atom()


@app.teardown_request
def shutdown_session(exception=None):
    db_session.close()
