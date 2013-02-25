import os

_basedir = os.path.abspath(os.path.dirname(__file__))

FLASK_OPTIONS = {'debug': True}

DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'db.sqlite')
DATABASE_OPTIONS = {
    'convert_unicode': True,
    'echo': False}

del os
