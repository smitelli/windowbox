from __future__ import absolute_import
from flask import jsonify, make_response
from windowbox.views.error import ErrorView
from windowbox.views.page import PageView


class ErrorHandler(object):
    @classmethod
    def get(cls, error, as_json=False):
        render = cls._render_json if as_json else cls._render_html

        return render(error)

    @staticmethod
    def _render_html(error):
        body_html = ErrorView(error=error).render_html()

        page_html = PageView(title=error.name, body=body_html).render_html()

        return make_response(page_html, error.code)

    @staticmethod
    def _render_json(error):
        response = jsonify(error=error.code, title=error.name)
        response.status_code = error.code

        return response
