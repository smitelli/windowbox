"""
Windowbox test configuration file.

These values are used when the application is run via `flask test`. It inherits
all values defined in base.py.
"""

from windowbox.configs.base import varpath

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(varpath / 'test.sqlite')
TESTING = True

THIS_IS_A_TEST_FIXTURE = 'PASSED'
