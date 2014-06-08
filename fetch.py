from windowbox.models.imap import IMAPManager


mgr = IMAPManager('imap.gmail.com', '', '')
for i in mgr.scrape_mailbox('Inbox'):
    print i.message_body
