from os import path

# This is the absolute, real path to the project directory
_base = path.abspath(path.join(path.dirname(__file__), '..'))


class AppPath(object):
    """Collection of class methods to build paths relative to any directory."""

    @classmethod
    def static(cls, subpath=''):
        return path.join(_base, 'static', subpath)

    @classmethod
    def windowbox(cls, subpath=''):
        return path.join(_base, 'windowbox', subpath)

    @classmethod
    def configs(cls, subpath=''):
        return path.join(_base, 'windowbox', 'configs', subpath)

    @classmethod
    def handlers(cls, subpath=''):
        return path.join(_base, 'windowbox', 'handlers', subpath)

    @classmethod
    def models(cls, subpath=''):
        return path.join(_base, 'windowbox', 'models', subpath)

    @classmethod
    def templates(cls, subpath=''):
        return path.join(_base, 'windowbox', 'templates', subpath)

    @classmethod
    def views(cls, subpath=''):
        return path.join(_base, 'windowbox', 'views', subpath)
