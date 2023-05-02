"""
Main Flask application for Windowbox.

This application accepts an optional (but highly suggested) `WINDOWBOX_CONFIG`
environment variable. This is interpreted as a filename containing configuration
variables that augment those in windowbox.configs.base.

Attributes:
    __version__: Semantic version number of this release of the application.
    app: The fully-configured Flask app suitable for WSGI, etc.
"""

import windowbox.blueprints.api as api_bp
import windowbox.blueprints.site as site_bp
import windowbox.utils
from datetime import datetime
from flask import Flask, request
from flask_assets import Environment
from functools import partial
from pathlib import Path
from werkzeug.exceptions import NotFound
from windowbox.clients.exiftool import ExifToolClient
from windowbox.clients.gmapi import GoogleMapsAPIClient
from windowbox.clients.imap import IMAP_SSLClient
from windowbox.clients.twitter import TwitterClient
from windowbox.database import db
from windowbox.models import import_all_models

__version__ = '3.0.0'

app = Flask(__name__)
app.config.from_pyfile('configs/base.py')
app.config.from_envvar('WINDOWBOX_CONFIG')
app.logger.handlers[0].setFormatter(app.config['APP_LOG_FORMATTER'])
app.logger.setLevel(app.config['APP_LOG_LEVEL'])

app.attachments_path = Path(app.config['ATTACHMENTS_PATH'])
app.derivatives_path = Path(app.config['DERIVATIVES_PATH'])
app.exiftool_client = ExifToolClient(exiftool_bin=app.config['EXIFTOOL_BIN'])
app.gmapi_client = GoogleMapsAPIClient(api_key=app.config['GOOGLE_MAPS_API_KEY'])
app.imap_client = IMAP_SSLClient(
    host=app.config['IMAP_FETCH_HOST'], user=app.config['IMAP_FETCH_USER'],
    password=app.config['IMAP_FETCH_PASSWORD'])
app.twitter_client = TwitterClient(
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
    access_token=app.config['TWITTER_ACCESS_TOKEN'],
    access_token_secret=app.config['TWITTER_ACCESS_TOKEN_SECRET'])

import_all_models()
db.init_app(app)

Environment(app)

site_bp.register(app)
api_bp.register(app)


@app.after_request
def prepare_response(response):
    """
    Manipulate the response before returning it.

    Current manipulations include:
      - Adding a custom response header for cool people to discover.
      - Minifying the response data if its content type is supported.

    Args:
        response: Instance of flask.wrappers.Response on its way to the client.

    Returns:
        Same as `response`, but with its headers and/or body modified.
    """
    response.headers['X-George-Carlin'] = 'I put a dollar in a change machine. Nothing changed.'

    minifier = None
    if response.content_type.startswith('text/html'):
        app.logger.debug('Using HTML minifier')
        minifier = windowbox.utils.minify_html
    elif response.content_type.startswith('application/xml'):
        app.logger.debug('Using XML minifier')
        minifier = partial(windowbox.utils.minify_xml, encoding='utf-8')

    if minifier is not None:
        body = response.get_data(as_text=True)
        body = minifier(body)
        response.set_data(body)

    return response


@app.errorhandler(NotFound)
def not_found_error(exc):
    """
    App-wide "not found" handler.

    Flask blueprints are a little odd in that they don't own the entire path
    space of their URL prefix. If a no-route-matched 404 occurs, Flask doesn't
    attempt to guess which blueprint the client was aiming for and everything
    ends up here. We manually try to guess the blueprint and dispatch to the
    correct error handler.
    """
    if request.path.startswith('/api'):
        app.logger.debug('Using api 404 handler')
        return api_bp.http_error(exc)
    else:
        app.logger.debug('Using site 404 handler')
        return site_bp.http_error(exc)


@app.context_processor
def template_globals():
    """
    Define custom global variables for use in the templates.
    """
    return {
        'copyright_from': 2004,
        'copyright_to': datetime.now().year,
        'generator_url': 'https://github.com/smitelli/windowbox',
        'generator_version': __version__,
        'site_title': 'Windowbox',
        'tagline': "Don't call it a moblog / I've posted for years."}


@app.template_filter()
def rfc2822format(dt):
    """
    Wrap the RFC 2822 formatter utility in a template filter.
    """
    return windowbox.utils.datetime_to_rfc2822(dt)


import windowbox.cli  # noqa: E402
