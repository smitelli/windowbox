from datetime import datetime
from flask import g


class AppGlobals(object):
    @classmethod
    def set_globals(cls):
        g.copyright_year = datetime.now().year

    @classmethod
    def init_app(cls, app):
        app.before_request(cls.set_globals)
