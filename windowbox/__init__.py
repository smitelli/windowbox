from os import path

# This is the absolute, real path to the package directory
_base = path.abspath(path.join(path.dirname(__file__)))


class AppPath(object):
    """Collection of class methods to build paths relative to any directory."""

    @classmethod
    def windowbox(cls, subpath=''):
        return cls._join(_base, subpath)

    @classmethod
    def configs(cls, subpath=''):
        return cls._join(_base, 'configs', subpath)

    @classmethod
    def handlers(cls, subpath=''):
        return cls._join(_base, 'handlers', subpath)

    @classmethod
    def models(cls, subpath=''):
        return cls._join(_base, 'models', subpath)

    @classmethod
    def static(cls, subpath=''):
        return cls._join(_base, 'static', subpath)

    @classmethod
    def templates(cls, subpath=''):
        return cls._join(_base, 'templates', subpath)

    @classmethod
    def views(cls, subpath=''):
        return cls._join(_base, 'views', subpath)

    @staticmethod
    def _join(*args):
        """Wrapper for path.join() that will always strip trailing slash."""
        joined = path.join(*args)
        return joined.rstrip('/\\')
