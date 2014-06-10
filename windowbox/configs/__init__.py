from __future__ import absolute_import
import pytz
from os import path
from windowbox.application import app


class BaseConfig(object):
    DEBUG = True
    TESTING = False
    SERVER_NAME = 'tarvos-ubuntu:5000'
    PREFERRED_URL_SCHEME = 'http'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(app.instance_path, 'db.sqlite')
    SQLALCHEMY_ECHO = False

    LISTEN_INTERFACE = '0.0.0.0'
    LISTEN_PORT = 5000
    BASE_HREF = '{}://{}'.format(PREFERRED_URL_SCHEME, SERVER_NAME)

    DISPLAY_TIMEZONE = pytz.timezone('America/New_York')

    STORAGE_DIR = path.join(app.instance_path, 'storage')

    EXIFTOOL = '/usr/bin/exiftool'

    ALLOWED_DIMENSIONS = [
        '300x300',
        '960x720']
