from windowbox.models.imap import IMAPManager


mgr = IMAPManager('imap.gmail.com', '', '')
for i in mgr.scrape_mailbox('Inbox', delete=False):

    print i.message_body
    print i.created_utc
    print i.sender
    print i.user_agent

    at = i.get_attachment_data('image/jpeg')
    if at:
        print len(at)
