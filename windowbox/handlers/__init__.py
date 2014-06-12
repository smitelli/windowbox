from datetime import datetime
from flask import g


class AppGlobals(object):
    def set_globals(cls):
        g.copyright_year = datetime.now().year

    def init_app(cls, app):
        app.before_request(cls.set_globals)


app_globals = AppGlobals()
