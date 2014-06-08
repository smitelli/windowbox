from windowbox.models.attachment import Attachment
from windowbox.models.imap import IMAPManager
from windowbox.models.post import Post


imap_manager = IMAPManager('imap.gmail.com', '', '')
messages = imap_manager.scrape_mailbox('Inbox')

for message in messages:
    real_name, email = message.sender
    if email != 'scott@smitelli.com':
        print 'Skipping, {} is not a permitted sender'.format(email)
        continue

    valid_types = Attachment.mime_extension_map.keys()
    attach_data = message.get_attachment_data(valid_types)

    if not attach_data:
        print 'Skipping, no usable attachment'
        continue

    post_data = {
        'created_utc': message.created_utc,
        'message': message.message_body,
        'user_agent': message.user_agent}
    post = Post(**post_data).save(commit=True)

    attachment = Attachment(post_id=post.id)
    attachment.set_data(attach_data)
    attachment.save(commit=True)

    print 'ok'

imap_manager.close()
