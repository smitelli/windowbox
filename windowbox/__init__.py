from os import path

# This is the absolute, real path to the 'windowbox' directory
_src = path.abspath(path.dirname(__file__))


class AppPath(object):
    """Collection of class methods to build paths relative to any directory."""

    @classmethod
    def windowbox(cls, subpath):
        return path.join(_src, subpath)

    @classmethod
    def configs(cls, subpath):
        return path.join(_src, 'configs', subpath)

    @classmethod
    def handlers(cls, subpath):
        return path.join(_src, 'handlers', subpath)

    @classmethod
    def models(cls, subpath):
        return path.join(_src, 'models', subpath)

    @classmethod
    def templates(cls, subpath):
        return path.join(_src, 'templates', subpath)

    @classmethod
    def views(cls, subpath):
        return path.join(_src, 'views', subpath)
