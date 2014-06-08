import email
import imaplib
import pytz
from collections import defaultdict
from datetime import datetime
from email.utils import mktime_tz, parsedate_tz

imap_session = imaplib.IMAP4_SSL('imap.gmail.com')

(typ, _) = imap_session.login('', '')
if typ != 'OK':
    raise Exception

imap_session.select('[Gmail]/All Mail')

(typ, results) = imap_session.uid('SEARCH', None, 'ALL')
if typ != 'OK':
    raise Exception

for uid in results[0].split():
    (typ, parts) = imap_session.uid('FETCH', uid, '(BODY[])')
    if typ != 'OK':
        raise Exception

    message = email.message_from_string(parts[0][1])

    created_utc = datetime.fromtimestamp(mktime_tz(parsedate_tz(message.get('date'))), pytz.utc)
    user_agent = message.get('x-mailer')
    message_body = defaultdict(str)
    attachments = []

    for part in message.walk():
        if part.is_multipart():
            continue

        if part.get('content-disposition') is None:
            ctype = str(part.get_content_type())
            charset = str(part.get_content_charset())
            payload = part.get_payload(decode=True)

            message_body[ctype] += payload.decode(charset, errors='replace')
        else:
            attachments.append(part)

imap_session.close()
imap_session.logout()
