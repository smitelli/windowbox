import os

_confdir = os.path.abspath(os.path.dirname(__file__))

FLASK_CONFIG = {
    'debug': True,
    'host': '0.0.0.0'}

DATABASE_CONFIG = {
    'URI': 'sqlite:///' + os.path.join(_confdir, '..', '..', 'db.sqlite'),
    'KWARGS': {
        'convert_unicode': True,
        'echo': False}}

STORAGE_DIR = os.path.abspath(os.path.join(_confdir, '..', '..', 'storage'))
