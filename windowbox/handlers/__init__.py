import collections
from datetime import datetime
from flask import abort, g, request


class AppGlobals(object):
    def set_globals(self):
        g.copyright_year = datetime.now().year

    def init_app(self, app):
        app.before_request(self.set_globals)


def get_or_404(method, *args, **kwargs):
    result = method(*args, **kwargs)

    if result is None:
        abort(404)

    if isinstance(result, collections.Iterable) and not any(result):
        abort(404)

    return result


def request_wants_json():
    json_score = request.accept_mimetypes['application/json']
    html_score = request.accept_mimetypes['text/html']

    return json_score > html_score


app_globals = AppGlobals()
