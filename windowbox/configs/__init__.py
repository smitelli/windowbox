from __future__ import absolute_import
import pytz
from windowbox import AppPath


class BaseConfig(object):
    DEBUG = True
    TESTING = False
    SERVER_NAME = 'tarvos-ubuntu:5000'
    PREFERRED_URL_SCHEME = 'http'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + AppPath.package('../db.sqlite')
    SQLALCHEMY_ECHO = False

    LISTEN_INTERFACE = '0.0.0.0'
    LISTEN_PORT = 5000
    BASE_HREF = '{}://{}'.format(PREFERRED_URL_SCHEME, SERVER_NAME)

    DISPLAY_TIMEZONE = pytz.timezone('America/New_York')

    STORAGE_DIR = AppPath.package('../storage')

    EXIFTOOL = '/usr/bin/exiftool'

    ALLOWED_DIMENSIONS = [
        '300x300',
        '960x720']
