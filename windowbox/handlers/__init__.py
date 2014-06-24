import collections
from datetime import datetime
from flask import abort, current_app, g, request


class AppGlobals(object):
    def set_globals(self):
        g.copyright_year = datetime.now().year

    def set_headers(self, response):
        response.headers['X-George-Carlin'] = "I put a dollar in a change machine. Nothing changed."

        return response

    def init_app(self, app):
        app.before_request(self.set_globals)
        app.after_request(self.set_headers)


app_globals = AppGlobals()


def request_wants_json():
    json_score = request.accept_mimetypes['application/json']
    html_score = request.accept_mimetypes['text/html']

    return json_score > html_score


def get_or_404(method, *args, **kwargs):
    result = method(*args, **kwargs)

    if result is None:
        current_app.logger.debug('Bailing with 404; result is None')
        abort(404)

    if isinstance(result, collections.Iterable) and not any(result):
        current_app.logger.debug('Bailing with 404; result Iterable has no truthy items')
        abort(404)

    return result
