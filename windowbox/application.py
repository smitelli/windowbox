from flask import Flask, request
from windowbox.database import db

app = Flask(__name__)
app.config.from_object('windowbox.configs.BaseConfiguration')
db.init_app(app)


def start_app():
    app.run(host=app.config['LISTEN_INTERFACE'], port=app.config['LISTEN_PORT'])
    return app


def request_wants_json():
    json_score = request.accept_mimetypes['application/json']
    html_score = request.accept_mimetypes['text/html']
    return json_score > html_score


@app.errorhandler(404)
def page_not_found(error):
    from windowbox.handlers.error import ErrorHandler
    return ErrorHandler.get(error, as_json=request_wants_json())


@app.route('/')
def get_index():
    from windowbox.handlers.index import IndexHandler
    until_id = request.args.get('until')
    return IndexHandler.get(until_id=until_id, as_json=request_wants_json())


@app.route('/post/<int:post_id>')
def get_post(post_id):
    from windowbox.handlers.post import PostHandler
    return PostHandler.get(post_id, as_json=request_wants_json())


@app.route('/attachment/<int:attachment_id>')
@app.route('/attachment/<int:attachment_id>/<dimensions>')
def get_attachment_derivative(attachment_id, dimensions=''):
    from windowbox.handlers.attachment import AttachmentDerivativeHandler
    allow_crop = False if request.args.get('crop') == 'false' else True
    return AttachmentDerivativeHandler.get(attachment_id, dimensions=dimensions, allow_crop=allow_crop)


@app.route('/rss.xml')
def get_rss2():
    from windowbox.handlers.feed import FeedHandler
    return FeedHandler.get_rss2()


@app.route('/atom.xml')
def get_atom():
    from windowbox.handlers.feed import FeedHandler
    return FeedHandler.get_atom()
