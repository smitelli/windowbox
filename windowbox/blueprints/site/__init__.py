"""
Flask blueprint for HTML site routes.

Attributes:
    X_ACCEL_REDIRECT_ROOT: When using X-Accel-Redirect, this is the path prefix
        that will be used to refer to the Derivative files. Should not have a
        trailing slash!
    bp: Blueprint object containing all site endpoints and handlers.
    logger: Logger instance scoped to the current module name.
"""

import logging
from flask import (
    Blueprint, abort, current_app, make_response, render_template, request, send_file)
from flask_assets import Bundle
from http import HTTPStatus
from werkzeug.exceptions import HTTPException
from windowbox.controllers.attachment import AttachmentController
from windowbox.controllers.post import PostController

X_ACCEL_REDIRECT_ROOT = '/_derivatives'

bp = Blueprint('site', __name__, template_folder='templates')
logger = logging.getLogger(__name__)


def register(app):
    """
    Register this blueprint on a Flask app instance.

    This function assumes the app has a Flask-Webassets environment set up on it
    already.

    Args:
        app: Instance of the Flask application.
    """
    app.register_blueprint(bp)

    assets = app.jinja_env.assets_environment

    assets.register('site_css', Bundle(
        'scss/site.scss', filters='libsass', output='site.dist.css'))
    assets.register('site_js', Bundle(
        'js/vendor/jquery-2.2.4.min.js', 'js/vendor/imagesloaded-4.1.4.min.js',
        'js/site.js', filters='rjsmin', output='site.dist.js'))


@bp.errorhandler(HTTPException)
def http_error(exc):
    """
    Display the friendly error page for any unhandled HTTP exceptions.
    """
    if 500 <= exc.code <= 599:  # pragma: nocover
        logger.exception(f'HTTP {exc.code} response generated!')

    return render_template('error.html', error_exc=exc), exc.code


@bp.route('/')
def get_index():
    """
    Handler for the index (landing) page.
    """
    try:
        posts, has_more, page_mode = PostController.get_many(
            since_id=request.args.get('since'),
            until_id=request.args.get('until'),
            limit=PostController.SITE_DEFAULT_LIMIT)
    except PostController.InvalidArgument:
        abort(HTTPStatus.UNPROCESSABLE_ENTITY)

    since_id = None
    until_id = None
    if has_more:
        if page_mode == PostController.PAGE_MODE.SINCE:
            since_id = posts[-1].id
        elif page_mode == PostController.PAGE_MODE.UNTIL:
            until_id = posts[-1].id

    return render_template(
        'index.html', posts=posts, has_more=has_more,
        since_id=since_id, until_id=until_id)


@bp.route('/post/<int:post_id>')
def get_post(post_id):
    """
    Handler for individual Post pages.
    """
    try:
        post, older, newer = PostController.get_by_id(post_id)
    except PostController.NoResultFound:
        abort(HTTPStatus.NOT_FOUND)

    return render_template(
        'post.html', post=post, older_post=older, newer_post=newer)


@bp.route('/attachment/<int:attachment_id>/<dimensions>')
def get_attachment_derivative(attachment_id, dimensions):
    """
    Handler for individual Attachment image files.

    Note that Attachments are never actually returned -- the actual data comes
    from a Derivative which uses the specified Attachment as its source.
    """
    try:
        derivative = AttachmentController.get_attachment_derivative(
            attachment_id=attachment_id, dimensions=dimensions)
    except AttachmentController.NoResultFound:
        abort(HTTPStatus.NOT_FOUND)

    if current_app.config['USE_X_ACCEL_REDIRECT']:
        # Rewrite the Derivative's storage path to refer to the nginx alias
        dv_base = str(derivative.base_path)
        dv_path = str(derivative.storage_path())
        redirect_path = f'{X_ACCEL_REDIRECT_ROOT}{dv_path[len(dv_base):]}'

        logger.debug(
            f'Sending Derivative ID {derivative.id} with '
            f'X-Accel-Redirect: {redirect_path}')

        return make_response(b'', {
            'X-Accel-Redirect': redirect_path,
            'Content-Type': derivative.mime_type})
    else:
        logger.debug(f'Sending Derivative ID {derivative.id} with send_file()')

        return send_file(derivative.storage_path(), mimetype=derivative.mime_type)


@bp.route('/atom.xml')
def get_feed_atom():
    """
    Handler for the Atom feed.
    """
    lastmod = PostController.get_lastmod_datetime()
    posts, *_ = PostController.get_many(limit=PostController.ATOM_LIMIT)

    return make_response(
        render_template('feed_atom.xml', posts=posts, updated=lastmod),
        {'Content-Type': 'application/xml; charset=utf-8'})


@bp.route('/rss.xml')
def get_feed_rss():
    """
    Handler for the XML feed.
    """
    lastmod = PostController.get_lastmod_datetime()
    posts, *_ = PostController.get_many(limit=PostController.RSS_LIMIT)

    return make_response(
        render_template(
            'feed_rss.xml', posts=posts, pub_date=lastmod, last_build_date=lastmod),
        {'Content-Type': 'application/xml; charset=utf-8'})


@bp.route('/sitemap.xml')
def get_feed_sitemap():
    """
    Handler for the XML sitemap.
    """
    lastmod = PostController.get_lastmod_datetime()
    posts = PostController.yield_all()

    return make_response(
        render_template('feed_sitemap.xml', posts=posts, lastmod=lastmod),
        {'Content-Type': 'application/xml; charset=utf-8'})


@bp.route('/health-check')
def get_health_check():
    """
    Handler for simple "I'm alive" endpoint.
    """
    return 'OK', {'Content-Type': 'text/plain; charset=utf-8'}
