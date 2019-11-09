"""
Windowbox IMAP fetch script.

This should usually be called via the console script defined in setup.py:

    WINDOWBOX_CONFIG=configs/some.py windowbox-fetch

It can also be run directly from a suitable Python interpreter:

    WINDOWBOX_CONFIG=configs/some.py python windowbox/fetch.py

This script scrapes the IMAP mailbox specified in the config file, considers
each message it finds within, and passes suitable ones on to be ingested as
Posts and Attachments. Unsuitable messages are not ingested. All messages, once
considered, are deleted from the mailbox.

Attributes:
    logger: Logger instance scoped to the current module name.
"""

import logging
import sys
from windowbox import app
from windowbox.clients.imap import NoMessages
from windowbox.controllers.attachment import AttachmentController
from windowbox.controllers.post import PostController
from windowbox.database import db

logger = logging.getLogger(__name__)


def main():
    """
    Main entrypoint for the windowbox-fetch console script.

    Returns:
        0, unless something raises an uncaught exception.
    """
    logger.info('Starting windowbox-fetch')

    with app.app_context():
        run_fetch(
            attachments_path=app.attachments_path,
            exiftool_client=app.exiftool_client,
            gmapi_client=app.gmapi_client,
            imap_client=app.imap_client)

    logger.info('windowbox-fetch completed without error')

    return 0


def run_fetch(*, attachments_path, exiftool_client, gmapi_client, imap_client):
    """
    Actual fetch-and-create function.

    Args:
        attachments_path: A pathlib Path object that points to the root
            directory where storage data for Attachments should be saved.
        exiftool_client: Instance of ExifToolClient configured to read EXIF
            metadata from files.
        gmapi_client: Instance of GoogleMapsAPIClient configured with a valid
            Google Maps API key.
        imap_client: Instance of IMAP_SSLClient configured with the desired
            email authentication and mailbox values.
    """
    try:
        for message in imap_client.yield_messages():
            logger.info(
                f'Processing message UID {int(message.uid)}, ID {message.message_id}')

            try:
                post = PostController.message_to_post(message)
            except PostController.UnknownSender:
                logger.warning(
                    f'Unknown sender {message.from_name} <{message.from_address}>; '
                    'deleting message')
                message.delete()
                continue

            db.session.add(post)

            for mime_type, data in AttachmentController.message_to_data(message):
                logger.debug(f'Got attachment type {mime_type}')

                attachment = post.new_attachment(mime_type=mime_type)
                db.session.add(attachment)
                db.session.flush()

                attachment.base_path = attachments_path
                attachment.set_storage_data(data)
                attachment.populate_exif(exiftool_client=exiftool_client)
                attachment.populate_geo(gmapi_client=gmapi_client)

            db.session.commit()
            message.delete()
    except NoMessages:
        logger.info('There are no messages')


if __name__ == '__main__':  # pragma: nocover
    sys.exit(main())
