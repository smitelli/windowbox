from __future__ import absolute_import
import logging
from windowbox.application import app
from windowbox.models.attachment import Attachment
from windowbox.models.imap import IMAPManager
from windowbox.models.post import Post

with app.app_context():
    if not app.debug:
        handler = logging.FileHandler(app.config['FETCH_LOG'])
        handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.DEBUG)

    app.logger.info('Checking for new IMAP messages')

    valid_types = Attachment.MIME_EXTENSION_MAP.keys()
    connect_kwargs = {
        'host': app.config['IMAP_HOST'],
        'port': app.config['IMAP_PORT'],
        'user': app.config['IMAP_USER'],
        'password': app.config['IMAP_PASSWORD']}

    imap_manager = IMAPManager(**connect_kwargs)
    messages = imap_manager.scrape_mailbox(app.config['IMAP_MAILBOX'])

    for message in sorted(messages):
        app.logger.info('Message ID %s, sent on %s', message.message_id, message.created_utc)

        real_name, email = message.sender
        if email not in app.config['IMAP_ALLOWED_FROM']:
            app.logger.error('Skipping, %s is not a permitted sender', email)
            continue

        attach_data = message.get_attachment_data(valid_types)
        if not attach_data:
            app.logger.error('Skipping, no usable attachment')
            continue

        post_kwargs = {
            'created_utc': message.created_utc,
            'message': message.message_body,
            'user_agent': message.user_agent}

        app.logger.debug('Inserting post data: %s', repr(post_kwargs))
        post = Post(**post_kwargs).save(commit=True)

        app.logger.debug('Inserting attachment: <%s bytes>', len(attach_data))
        attachment = Attachment(post_id=post.id)
        attachment.set_data(attach_data)
        attachment.save(commit=True)

        app.logger.info('Created post #%d, attachment #%d', post.id, attachment.id)

    imap_manager.close()
    app.logger.info('Check has finished')
