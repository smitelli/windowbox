from __future__ import absolute_import
import logging
from flask import Flask, request
from windowbox.database import db
from windowbox.handlers import app_globals, request_wants_json
from windowbox.handlers.attachment import AttachmentDerivativeHandler
from windowbox.handlers.error import ErrorHandler
from windowbox.handlers.feed import FeedHandler
from windowbox.handlers.index import IndexHandler
from windowbox.handlers.post import PostHandler

app = Flask(__name__)
app.config.from_object('windowbox.configs.BaseConfig')
app.config.from_envvar('WINDOWBOX_CONFIG_FILE', silent=True)

if not app.debug:
    handler = logging.FileHandler(app.config['APPLICATION_LOG'])
    handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    app.logger.info('Sending log output to %s', app.config['APPLICATION_LOG'])
else:
    app.logger.info('Sending log output to standard error')

db.init_app(app)
app_globals.init_app(app)


def start_app():
    app.run(host=app.config['LISTEN_INTERFACE'], port=app.config['LISTEN_PORT'])
    return app


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(Exception)
def error_handler(error):
    return ErrorHandler.get(error, as_json=request_wants_json())


@app.route('/')
def get_index():
    since_id = request.args.get('since')
    until_id = request.args.get('until')
    return IndexHandler.get(since_id=since_id, until_id=until_id, as_json=request_wants_json())


@app.route('/post/<int:post_id>')
def get_post(post_id):
    return PostHandler.get(post_id, as_json=request_wants_json())


@app.route('/attachment/<int:attachment_id>')
@app.route('/attachment/<int:attachment_id>/<dimensions>')
def get_attachment_derivative(attachment_id, dimensions=''):
    return AttachmentDerivativeHandler.get(attachment_id, dimensions=dimensions)


@app.route('/rss.xml')
def get_rss2():
    return FeedHandler.get_rss2()


@app.route('/atom.xml')
def get_atom():
    return FeedHandler.get_atom()


@app.route('/sitemap.xml')
def get_sitemap():
    return FeedHandler.get_sitemap()
