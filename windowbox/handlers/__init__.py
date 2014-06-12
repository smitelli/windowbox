import collections
from datetime import datetime
from flask import abort, g


class AppGlobals(object):
    def set_globals(cls):
        g.copyright_year = datetime.now().year

    def init_app(cls, app):
        app.before_request(cls.set_globals)


def get_or_404(method, *args, **kwargs):
    result = method(*args, **kwargs)

    if result is None:
        abort(404)

    if isinstance(result, collections.Iterable) and not any(result):
        abort(404)

    return result


app_globals = AppGlobals()
