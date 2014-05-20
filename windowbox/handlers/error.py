from flask import make_response
from windowbox.views.error import ErrorView
from windowbox.views.page import PageView


class ErrorHandler():
    @classmethod
    def get(cls, code=500):
        try:
            title = {
                404: 'Not Found',
                500: 'Internal Server Error'
            }[code]
        except KeyError:
            title = None

        body_html = ErrorView(title=title, code=code).render_html()

        page_html = PageView(title=title, body=body_html).render_html()

        return make_response(page_html, code)
