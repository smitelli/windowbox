import imaplib
import email
import pytz
from datetime import datetime

imapSession = imaplib.IMAP4_SSL('imap.gmail.com')

(typ, _) = imapSession.login('', '')
if typ != 'OK':
    raise Exception

imapSession.select('[Gmail]/All Mail')

(typ, results) = imapSession.uid('SEARCH', None, 'ALL')
if typ != 'OK':
    raise Exception

for uid in results[0].split():
    (typ, parts) = imapSession.uid('FETCH', uid, '(BODY[])')
    if typ != 'OK':
        raise Exception

    message = email.message_from_string(parts[0][1])

    created_utc = datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(message.get('date'))), pytz.utc)
    user_agent = message.get('x-mailer')
    message_body = {}
    attachments = []

    for part in message.walk():
        if part.is_multipart():
            continue

        if part.get('content-disposition') is None:
            ctype = str(part.get_content_type())
            charset = str(part.get_content_charset())
            payload = part.get_payload(decode=True)

            if ctype not in message_body:
                message_body[ctype] = ''

            message_body[ctype] += unicode(payload, encoding=charset, errors='ignore').encode('utf8', errors='replace')
        else:
            attachments.append(part)

imapSession.close()
imapSession.logout()
