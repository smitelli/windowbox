import os

_basedir = os.path.abspath(os.path.dirname(__file__))

FLASK_OPTIONS = {'debug': True, 'host': '0.0.0.0'}

DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'db.sqlite')
DATABASE_OPTIONS = {
    'convert_unicode': True,
    'echo': True}

del os
