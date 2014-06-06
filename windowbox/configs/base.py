import pytz
from windowbox import AppPath


FLASK_KWARGS = {
    'debug': True,
    'host': '0.0.0.0'}

DATABASE_URI = 'sqlite:///' +  AppPath.package('../db.sqlite')
DATABASE_KWARGS = {
    'convert_unicode': True,
    'echo': False}

BASE_HREF = 'http://tarvos-ubuntu:5000'

DISPLAY_TIMEZONE = pytz.timezone('America/New_York')

STORAGE_DIR = AppPath.package('../storage')

EXIFTOOL = '/usr/bin/exiftool'

ALLOWED_DIMENSIONS = [
    '300x300',
    '960x720']
