from __future__ import absolute_import
import traceback
from flask import current_app, jsonify, make_response
from werkzeug.exceptions import HTTPException, InternalServerError
from windowbox.views.error import ErrorView
from windowbox.views.page import PageView


class ErrorHandler(object):
    @classmethod
    def get(cls, error, as_json=False):
        if not isinstance(error, HTTPException):
            error = InternalServerError()
            stack = traceback.format_exc()
            current_app.logger.debug('Got a non-HTTP exception; stack follows:\n%s', stack)
        else:
            stack = None
            current_app.logger.debug('Got an HTTPException')

        render = cls._render_json if as_json else cls._render_html

        return render(error, stack)

    @staticmethod
    def _render_html(error, stack):
        body_html = ErrorView(error=error, stack=stack).render_html()

        page_html = PageView(title=error.name, body=body_html).render_html()

        return make_response(page_html, error.code)

    @staticmethod
    def _render_json(error, stack):
        kwargs = {
            'error': error.code,
            'title': error.name}

        if current_app.debug and stack:
            current_app.logger.debug('Including the stack')
            kwargs['stack'] = stack

        response = jsonify(**kwargs)
        response.status_code = error.code

        return response