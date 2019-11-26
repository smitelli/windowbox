"""
Windowbox bark script.

This should usually be called via the console script defined in setup.py:

    WINDOWBOX_CONFIG=configs/some.py windowbox-bark

It can also be run directly from a suitable Python interpreter:

    WINDOWBOX_CONFIG=configs/some.py python windowbox/bark.py

This script searches for any Post instances that have not been "barked" (i.e.
posted to social media sites and third-party services) and handles each one.
After a Post is barked, its database record is updated so it does not come up
again during a future bark run.

Attributes:
    logger: Logger instance scoped to the current module name.
"""

import logging
import sys
from flask import url_for
from windowbox import app
from windowbox.controllers.post import PostController
from windowbox.database import db
from windowbox.utils import truncate_text

logger = logging.getLogger(__name__)


def main():
    """
    Main entrypoint for the windowbox-bark console script.

    Returns:
        0, unless something raises an uncaught exception.
    """
    logger.info('Starting windowbox-bark')

    # HACK: CLI usage has no understanding of the server name.
    app.config['SERVER_NAME'] = app.config['BARK_SERVER_NAME']

    with app.app_context():
        run_bark(
            twitter_client=app.twitter_client)

    logger.info('windowbox-bark completed without error')

    return 0


def run_bark(*, twitter_client):
    """
    Actual bark function.

    Args:
        twitter_client: Instance of a TwitterClient available for use.
    """
    max_length = None

    for post in PostController.yield_unbarked():
        logger.info(f'Barking Post ID {post.id}')

        if max_length is None:
            # Figure out how much room there is for the Post caption, accounting
            # for the length of Twitter's short URLs and the single space that
            # separates them.
            max_length = (twitter_client.status_length - twitter_client.url_length) - 1
            logger.debug(f'Tweet caption length is {max_length} chars')

        caption = truncate_text(post.caption, max_length)
        url = url_for('site.get_post', post_id=post.id, _external=True)
        status = f'{caption} {url}'

        response = twitter_client.update_status(status)
        logger.info(f'Tweet ID {response.id_str} created with: {response.text}')

        post.is_barked = True
        db.session.add(post)
        db.session.commit()


if __name__ == '__main__':  # pragma: nocover
    sys.exit(main())
