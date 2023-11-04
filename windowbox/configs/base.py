"""
Windowbox base configuration file.

This file defines every configuration value that is of interest to the
application. It sets safe (although generally not usable) default values for
each one. The expectation is that another environment-specific file will be
loaded to override values defined here.

Attributes:
    varpath: Base pathlib Path containing the root directory for local file and
        object storage. This is a somewhat reasonable default, but environment
        configs are free to disregard it entirely and do their own thing.
"""

import logging
from pathlib import Path

varpath = Path('/var/opt/windowbox')

"""
Used by multiple modules
"""
TESTING = False

"""
Flask
"""
PREFERRED_URL_SCHEME = 'http'

"""
Flask-Assets
"""
LIBSASS_STYLE = 'compressed'

"""
Flask-SQLAlchemy
"""
SQLALCHEMY_DATABASE_URI = ''
SQLALCHEMY_TRACK_MODIFICATIONS = False

"""
Windowbox app-specific
"""
APP_LOG_FORMATTER = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
APP_LOG_LEVEL = logging.INFO
ATTACHMENTS_PATH = str(varpath / 'attachments')
DERIVATIVES_PATH = str(varpath / 'derivatives')
EXIFTOOL_BIN = '/usr/bin/exiftool'
GOOGLE_MAPS_API_KEY = ''
IMAP_FETCH_HOST = ''
IMAP_FETCH_USER = ''
IMAP_FETCH_PASSWORD = ''
USE_X_ACCEL_REDIRECT = False
