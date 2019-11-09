"""
Windowbox development configuration file.

These values are used when the application is run via `flask run`. It inherits
all values defined in base.py.
"""

from windowbox.configs.base import varpath

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(varpath / 'dev.sqlite')
