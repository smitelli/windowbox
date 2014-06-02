from flask import make_response
from windowbox.views.error import ErrorView
from windowbox.views.page import PageView


class ErrorHandler():
    @classmethod
    def get(cls, error):
        try:
            title = {
                404: 'Not Found',
                500: 'Internal Server Error'
            }[error.code]
        except KeyError:
            title = None

        body_html = ErrorView(error=error, title=title).render_html()

        page_html = PageView(title=title, body=body_html).render_html()

        return make_response(page_html, error.code)
