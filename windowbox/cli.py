"""
Command-line scripts for Windowbox.

This file defines several custom commands for use with the `flask <COMMAND>`
utility. Broadly, these scripts can do the following:

    * Initialize, fill, and clear the development database.
    * Run development reports (style checks/unit tests).

Each script tries to be a courteous command-line citizen, implementing exit
codes and responding to `flask --help` in useful ways.

NOTE: The `flask` utility is sensitive to the current working directory. It
*MUST* be run from /vagrant or one of the subdirectories beneath or the
application code will not be properly detected.

Attributes:
    DEV_DB_SUFFIX: The expected value the database connection string should end
        with. If this suffix does not match, all scripts that manipulate the
        database will abort for safety.
    DEV_CLI_EMAIL_ADDRESS: Email address to use for the Sender in the
        `flask insert` command.
    DEV_CLI_DISPLAY_NAME: Display name to use for the Sender in the
        `flask insert` command.
    DEV_CLI_USER_AGENT: User-agent string to use for the Post in the
        `flask insert` command.
    FAKE_IMAGE_DIMENSIONS: Tuple containing the width, height of the "full"
        image in the `flask insert` command.
    CIRCLE_AREA: 4-tuple of (x1, y1, x2, y2) outlining the bounding box for the
        inner circle in the fake image (to visually verify cropping).
"""

import click
import os
import shutil
import sys
from subprocess import call
from windowbox import app
from windowbox.database import db

DEV_DB_SUFFIX = '/dev.sqlite'
DEV_CLI_EMAIL_ADDRESS = 'cli@localhost'
DEV_CLI_DISPLAY_NAME = 'Development User'
DEV_CLI_USER_AGENT = 'windowbox.cli'
FAKE_IMAGE_DIMENSIONS = (2000, 1500)
CIRCLE_AREA = (250, 0, 1750, 1499)


@app.cli.command('create')
def cli_create():  # pragma: nocover
    """
    Create all database tables defined by the app models.

    If the database already exists, this function is a no-op and will not harm
    any existing data that may be stored there.
    """
    if not app.config['SQLALCHEMY_DATABASE_URI'].endswith(DEV_DB_SUFFIX):
        raise EnvironmentError('Refusing to create a non-dev database')

    db.create_all()

    print('Dev database created.')


@app.cli.command('drop')
def cli_drop():  # pragma: nocover
    """
    Drop all database tables defined by the app models AND clear storage files.

    If the database does not exist, this function will succeed quietly.
    """
    if not app.config['SQLALCHEMY_DATABASE_URI'].endswith(DEV_DB_SUFFIX):
        raise EnvironmentError('Refusing to drop a non-dev database')

    db.drop_all()

    for d in (app.attachments_path, app.derivatives_path):
        shutil.rmtree(d)

    print('Dev database and storage files dropped.')


@app.cli.command('insert')
@click.argument('count', default=1, type=int)
def cli_insert(count):  # pragma: nocover
    """
    Generate COUNT Posts with Attachments and all other attributes filled in.

    If unspecified, COUNT defaults to 1.
    """
    import sqlalchemy.orm.exc
    from PIL import Image, ImageDraw
    from random import randrange
    from windowbox.models.post import Post
    from windowbox.models.sender import Sender

    print(f'Generating {count} Post(s)...')

    try:
        sender = Sender.query.filter_by(email_address=DEV_CLI_EMAIL_ADDRESS).one()
    except sqlalchemy.orm.exc.NoResultFound:
        sender = Sender(
            email_address=DEV_CLI_EMAIL_ADDRESS,
            display_name=DEV_CLI_DISPLAY_NAME)
        db.session.add(sender)
        print(f'Sender {DEV_CLI_EMAIL_ADDRESS} was created.')

    for _ in range(count):
        color = (randrange(256), randrange(256), randrange(256))
        fake_caption = f'#{color[0]:0>2X}{color[1]:0>2X}{color[2]:0>2X}'
        fake_image = Image.new('RGB', FAKE_IMAGE_DIMENSIONS, color)
        draw = ImageDraw.Draw(fake_image)
        draw.ellipse(CIRCLE_AREA, fill=(color[2], color[1], color[0]))

        post = Post(
            sender=sender,
            caption=fake_caption,
            user_agent=DEV_CLI_USER_AGENT)
        db.session.add(post)

        attachment = post.new_attachment(mime_type='image/jpeg')
        db.session.add(attachment)
        db.session.flush()

        attachment.base_path = app.attachments_path
        attachment.set_storage_data_from_image(fake_image)
        attachment.populate_exif(exiftool_client=app.exiftool_client)

        attachment.geo_latitude = attachment.exif['Composite:GPSLatitude.num'] = 36
        attachment.geo_longitude = attachment.exif['Composite:GPSLongitude.num'] = -78.9
        attachment.geo_address = 'Command Line, USA'

        db.session.commit()

        print(f'Post {post.id}: {fake_caption}')

    print('Done.')


@app.cli.command('lint')
def cli_lint():  # pragma: nocover
    """
    Lint the Python code using flake8.
    """
    retcode = call(['flake8'])

    if retcode == 0:
        print('No style problems found.')

    sys.exit(retcode)


@app.cli.command('test', context_settings={'ignore_unknown_options': True})
@click.argument('pytest_args', nargs=-1, type=click.UNPROCESSED)
def cli_test(pytest_args):  # pragma: nocover
    """
    Run the unit tests.

    If PYTEST_ARGS is provided, they will be passed to the test runner.
    """
    os.environ['WINDOWBOX_CONFIG'] = 'configs/test.py'

    sys.exit(call(['pytest', *pytest_args]))
