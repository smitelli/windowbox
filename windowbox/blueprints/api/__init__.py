"""
Flask blueprint for REST API routes.

Attributes:
    bp: Blueprint object containing all API endpoints and handlers.
    logger: Logger instance scoped to the current module name.
    api_url_for: Wrapper for Flask's url_for() that forces URLs to be external.
"""

import logging
from flask import Blueprint, abort, request, url_for
from functools import partial
from http import HTTPStatus
from werkzeug.exceptions import HTTPException
from windowbox.controllers.attachment import AttachmentController
from windowbox.controllers.post import PostController
from .schemas import AttachmentSchemaFull, PostSchema, PostSchemaFull

bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

api_url_for = partial(url_for, _external=True)


def register(app):
    """
    Register this blueprint on a Flask app instance.

    Args:
        app: Instance of the Flask application.
    """
    app.register_blueprint(bp)


@bp.errorhandler(HTTPException)
def http_error(exc):
    """
    Return the error structure for any unhandled HTTP exceptions.
    """
    if 500 <= exc.code <= 599:  # pragma: nocover
        logger.exception(f'HTTP {exc.code} response generated!')

    return {
        'error': {
            'status': exc.code,
            'message': exc.name,
            'details': exc.description}}, exc.code


@bp.route('/posts')
def get_many_posts():
    """
    Handler for returning a list of Posts matching the query arguments.

    Pagination is achieved by sending ONE of the following:
      - `since`: Only return Posts with IDs higher than this value, in
        ascending order.
      - `until`: Only return Posts with IDs lower than this value, in
        descending order. This is the default mode when requesting the first
        page of results.

    Additionally, accepts an optional `limit` argument in the range 1..100 to
    control how many objects to return. If omitted, the site default is used.
    """
    limit = request.args.get('limit')

    try:
        posts, has_more, page_mode = PostController.get_many(
            since_id=request.args.get('since'),
            until_id=request.args.get('until'),
            limit=limit or PostController.API_DEFAULT_LIMIT)
    except PostController.InvalidArgument:
        abort(HTTPStatus.UNPROCESSABLE_ENTITY)

    more_url = None
    if has_more:
        more_kwargs = {}
        if page_mode == PostController.PAGE_MODE.SINCE:
            more_kwargs['since'] = posts[-1].id
        elif page_mode == PostController.PAGE_MODE.UNTIL:
            more_kwargs['until'] = posts[-1].id

        if limit is not None:
            more_kwargs['limit'] = limit

        more_url = api_url_for('.get_many_posts', **more_kwargs)

    return {
        'posts': [PostSchema(p).to_dict() for p in posts],
        'more_url': more_url}


@bp.route('/posts/<int:post_id>')
def get_post(post_id):
    """
    Handler for individual Post lookups.
    """
    try:
        post, older, newer = PostController.get_by_id(post_id)
    except PostController.NoResultFound:
        abort(HTTPStatus.NOT_FOUND)

    older_url = None
    if older is not None:
        older_url = api_url_for('.get_post', post_id=older.id)

    newer_url = None
    if newer is not None:
        newer_url = api_url_for('.get_post', post_id=newer.id)

    return {
        'post': PostSchemaFull(post).to_dict(),
        'older_url': older_url,
        'newer_url': newer_url}


@bp.route('/attachments/<int:attachment_id>')
def get_attachment(attachment_id):
    """
    Handler for individual Attachment lookups.
    """
    try:
        attachment = AttachmentController.get_by_id(attachment_id)
    except AttachmentController.NoResultFound:
        abort(HTTPStatus.NOT_FOUND)

    return {
        'attachment': AttachmentSchemaFull(attachment).to_dict()}
