import os

_basedir = os.path.abspath(os.path.dirname(__file__))

FLASK_CONFIG = {'debug': True, 'host': '0.0.0.0'}

DATABASE_CONFIG = {
    'URI': 'sqlite:///' + os.path.join(_basedir, 'db.sqlite'),
    'KWARGS': {
        'convert_unicode': True,
        'echo': False}}
