from __future__ import absolute_import
import email
import imaplib
import re
import pytz
from collections import defaultdict
from datetime import datetime
from email.utils import mktime_tz, parseaddr, parsedate_tz


class IMAPException(Exception):
    pass


class IMAPManager(object):
    def __init__(self, host, user, password, port=993):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.session = imaplib.IMAP4_SSL(self.host, self.port)
        self.last_type = None

        self._do('LOGIN', user=self.user, password=self.password)

    def close(self):
        self.session.expunge()
        self.session.close()
        self.session.logout()

    def scrape_mailbox(self, mailbox, delete=True):
        self._do('SELECT', mailbox=mailbox)

        matches = self._do_uid('SEARCH', None, 'ALL')

        for uid in matches[0].split():
            parts = self._do_uid('FETCH', uid, '(BODY[])')
            message = email.message_from_string(parts[0][1])

            yield IMAPMessage(message)

            if delete:
                self._do_uid('STORE', uid, '+FLAGS', '\\Deleted')

    def _do(self, method, *args, **kwargs):
        try:
            fn = getattr(self.session, method)
        except AttributeError:
            raise IMAPException('No method {}'.format(method))

        (self.last_type, results) = fn(*args, **kwargs)
        if self.last_type != 'OK':
            raise IMAPException('Method {} returned {}'.format(method, self.last_type))

        return results

    def _do_uid(self, *args, **kwargs):
        return self._do('UID', *args, **kwargs)


class IMAPMessage(object):
    def __init__(self, message):
        self.message = message
        self.parts = self._read_body_parts(self.message)

    def __cmp__(self, other):
        return cmp(self.created_utc, other.created_utc)

    def __repr__(self):
        return '<{} message_id={}>'.format(self.__class__.__name__, self.message_id)

    @property
    def message_id(self):
        return self.message.get('message-id')

    @property
    def sender(self):
        return parseaddr(self.message.get('from'))

    @property
    def user_agent(self):
        return self.message.get('x-mailer')

    @property
    def created_utc(self):
        ts = mktime_tz(parsedate_tz(self.message.get('date')))
        return datetime.fromtimestamp(ts, pytz.utc)

    @property
    def message_body(self):
        return self.parts['text/plain'].strip_signature()

    def get_attachment_data(self, valid_types):
        if isinstance(valid_types, basestring):
            valid_types = [valid_types]

        for mime_type in valid_types:
            if mime_type in self.parts:
                return self.parts[mime_type].largest_payload()

        return None

    @staticmethod
    def _read_body_parts(message):
        body_parts = defaultdict(IMAPContent)

        for part in message.walk():
            if not part.is_multipart():
                content_type = part.get_content_type()
                body_parts[content_type].append(part)

        return body_parts


class IMAPContent(object):
    def __init__(self):
        self.is_attachment = False
        self.payloads = []

    def __repr__(self):
        return '<{} payloads={}>'.format(self.__class__.__name__, str(self.payloads))

    def append(self, part):
        payload = part.get_payload(decode=True)

        if part.get('content-disposition') is None:
            charset = part.get_content_charset()
            text = payload.decode(charset, errors='replace')
            self.payloads.append(self._normalize_crlf(text))
        else:
            self.is_attachment = True
            self.payloads.append(payload)

    def strip_signature(self):
        if self.is_attachment:
            raise IMAPException('Cannot strip an attachment')

        text = ''.join(self.payloads)
        text = re.split('^\s*-+\s*$', text, flags=re.MULTILINE)[0]

        return text.strip()

    def largest_payload(self):
        return max(self.payloads, key=len)

    @staticmethod
    def _normalize_crlf(text):
        return re.sub('\r\n', '\n', text)
