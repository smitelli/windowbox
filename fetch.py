from __future__ import absolute_import
from windowbox.application import app
from windowbox.models.attachment import Attachment
from windowbox.models.imap import IMAPManager
from windowbox.models.post import Post

with app.app_context():
    valid_types = Attachment.MIME_EXTENSION_MAP.keys()
    connect_kwargs = {
        'host': app.config['IMAP_HOST'],
        'port': app.config['IMAP_PORT'],
        'user': app.config['IMAP_USER'],
        'password': app.config['IMAP_PASSWORD']}

    imap_manager = IMAPManager(**connect_kwargs)
    messages = imap_manager.scrape_mailbox(app.config['IMAP_MAILBOX'])

    for message in sorted(messages):
        print 'Message ID {}, sent on {}'.format(message.message_id, message.created_utc)

        real_name, email = message.sender
        if email not in app.config['IMAP_ALLOWED_FROM']:
            print 'Skipping, {} is not a permitted sender'.format(email)
            continue

        attach_data = message.get_attachment_data(valid_types)
        if not attach_data:
            print 'Skipping, no usable attachment'
            continue

        post_kwargs = {
            'created_utc': message.created_utc,
            'message': message.message_body,
            'user_agent': message.user_agent}
        post = Post(**post_kwargs).save(commit=True)

        attachment = Attachment(post_id=post.id)
        attachment.set_data(attach_data)
        attachment.save(commit=True)

        print 'Inserted post #{}, attachment #{}'.format(post.id, attachment.id)

    imap_manager.close()
