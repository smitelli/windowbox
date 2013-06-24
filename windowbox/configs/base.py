import os
import pytz

_confdir = os.path.abspath(os.path.dirname(__file__))

FLASK_KWARGS = {
    'debug': True,
    'host': '0.0.0.0'}

DATABASE_CONFIG = {
    'URI': 'sqlite:///' + os.path.join(_confdir, '..', '..', 'db.sqlite'),
    'KWARGS': {
        'convert_unicode': True,
        'echo': False}}

DISPLAY_TIMEZONE = pytz.timezone('America/New_York')

STORAGE_DIR = os.path.abspath(os.path.join(_confdir, '..', '..', 'storage'))

EXIFTOOL = '/usr/local/bin/exiftool'
