from __future__ import absolute_import
from flask import jsonify, make_response
from windowbox.views.error import ErrorView
from windowbox.views.page import PageView


class ErrorHandler():
    @classmethod
    def get(cls, error, as_json=False):
        try:
            title = {
                404: 'Not Found',
                500: 'Internal Server Error'
            }[error.code]
        except KeyError:
            title = None

        render = cls._render_json if as_json else cls._render_html
        return render(error, title)

    @staticmethod
    def _render_html(error, title):
        body_html = ErrorView(error=error, title=title).render_html()

        page_html = PageView(title=title, body=body_html).render_html()

        return make_response(page_html, error.code)

    @staticmethod
    def _render_json(error, title):
        response = jsonify(error=error.code, title=title)
        response.status_code = error.code

        return response
