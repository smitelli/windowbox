from __future__ import absolute_import
import logging
import pytz
from os import path
from windowbox.application import app


class BaseConfig(object):
    DEBUG = True
    TESTING = False
    PREFERRED_URL_SCHEME = 'http'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(app.instance_path, 'db.sqlite')
    SQLALCHEMY_ECHO = False

    LISTEN_INTERFACE = '0.0.0.0'
    LISTEN_PORT = 5000

    LOG_FORMAT = '%(asctime)s %(module)s [%(levelname)s] %(message)s'
    LOG_LEVEL = logging.DEBUG
    APPLICATION_LOG = path.join(app.instance_path, 'application.log')
    FETCH_LOG = path.join(app.instance_path, 'fetch.log')

    IMAP_HOST = 'imap.gmail.com'
    IMAP_PORT = 993
    IMAP_USER = ''
    IMAP_PASSWORD = ''
    IMAP_MAILBOX = 'Inbox'
    IMAP_ALLOWED_FROM = ['scott@smitelli.com']

    DISPLAY_TIMEZONE = pytz.timezone('America/New_York')
    ALLOWED_DIMENSIONS = ['300x300', '960x720']

    STORAGE_DIR = path.join(app.instance_path, 'storage')
    EXIFTOOL = '/usr/bin/exiftool'
