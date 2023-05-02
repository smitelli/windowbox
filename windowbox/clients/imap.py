"""
IMAP4 client to fetch (and optionally delete) email messages in a sane way.

There are two components to this client: The IMAP_SSLClient, which connects to
an IMAP mailbox and iterates over all the messages found within it; and the
IMAPMessage, which represents a single email message within the mailbox and
provides methods to extract metadata, text, and attachments from it.

Attributes:
    UID_EXTRACTOR: Compiled regex used to locate a UID in an IMAP response.
    logger: Logger instance scoped to the current module name.
"""

import email
import email.policy
import email.utils
import imaplib
import logging
import re
import ssl
from collections import defaultdict
from operator import itemgetter

UID_EXTRACTOR = re.compile(rb'UID\s+(\d+)\s+')

logger = logging.getLogger(__name__)


class IMAPClientError(Exception):
    """
    Base exception class for any error that occurs within this client code.
    """
    pass


class NoMessages(IMAPClientError):
    """
    Indicates there are no messages to operate on.
    """
    pass


def check_restype(restype, exc_message):
    """
    Check that `restype` is "OK", otherwise raise with `exc_message`.

    Args:
        restype: Response type from the IMAP server.
        exc_message: If the response type is not satisfactory, use this as
            the message in the raised exception.

    Raises:
        IMAPError: The restype did not indicate success.
    """
    if restype != 'OK':
        raise IMAPClientError(exc_message)


class IMAP_SSLClient:
    """
    IMAP4 (SSL) email client.

    Attributes:
        DEFAULT_PORT: Value to be used for the `port` attribute of the
            constructor if unspecified. Set to the standard IMAP4 SSL port.
        DEFAULT_MAILBOX: Value to be used for the `mailbox` attribute of the
            yield_messages() method if unspecified. Set to "INBOX".
    """
    DEFAULT_PORT = imaplib.IMAP4_SSL_PORT
    DEFAULT_MAILBOX = 'INBOX'

    def __init__(self, *, host, port=DEFAULT_PORT, user, password):
        """
        Constructor.

        Args:
            host: The hostname (without protocol or port) of the IMAP4 server.
            port: The port of the IMAP4 server to connect to. If unspecified,
                uses the default.
            user: The user name or email address to send with the LOGIN command.
            password: The password to send with the LOGIN command.
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    @staticmethod
    def date_uid_map(data):
        """
        Parse IMAP response data and yield date/UID tuples.

        This is needed due to a few ugly aspects of IMAP and Gmail. There is no
        inherent order to IMAP UIDs, and Gmail doesn't have a native sort. On
        top of all that, the return value of a FETCH command has a very strange
        structure.

        This method expects zero or more message headers in the format returned
        by FETCH. It extracts the UID and the date (as a Python datetime) from
        each one, and yields tuples *in server-returned order* for each message.
        If sorting is desired, it's the caller's job to do that.

        Args:
            data: Raw response data from an IMAP FETCH command. Only needs to
                include the headers, but could optionally contain complete
                messages.

        Yields:
            Tuple of (date, uid) for each message encountered in the input.

        Raises:
            IMAPClientError: If the UID value could not be extracted.
        """
        for chunk in data:
            # Messages are terminated with a `)` byte that we can skip
            if not isinstance(chunk, tuple):
                continue

            # Extract the UID from the first part of the tuple
            match = UID_EXTRACTOR.search(chunk[0])
            if match is None:
                logger.debug(f'Could not find UID in: {chunk[0]}')
                raise IMAPClientError('could not find a UID')
            uid = match.group(1)

            # Parse the headers and extract the date from the second part
            msg = email.message_from_bytes(chunk[1], policy=email.policy.SMTP)
            if msg['date'] is None:
                logger.debug(f'Could not find a date header in UID {str(uid)}')
                raise IMAPClientError('could not find a date header')
            date = email.utils.parsedate_to_datetime(msg['date'])

            yield (date, uid)

    def yield_messages(self, *, mailbox=DEFAULT_MAILBOX):
        """
        Open up an IMAP mailbox and iterate over all messages found within.

        Messages do not need to be in an "unread" state to be found here; any
        message in the mailbox, regardless of age or read state, is considered.
        In order to prevent the same messages from being found again, they must
        be physically moved into a different mailbox or deleted.

        Args:
            mailbox: The name of the mailbox to use. If unspecified, uses the
                default.

        Yields:
           For each message discovered within the mailbox.

        Raises:
            NoMessages: There is nothing in the mailbox and no messages to
                yield. Some callers may prefer this condition to be expressed as
                an empty generator, but Windowbox likes this behavior.
        """
        with imaplib.IMAP4_SSL(
                host=self.host, port=self.port,
                ssl_context=ssl.create_default_context()) as ic:
            logger.debug(f'Logging in as {self.user}')
            restype, _ = ic.login(user=self.user, password=self.password)
            check_restype(restype, f'failed to LOGIN as {self.user}')

            logger.debug(f'Selecting mailbox {mailbox}')
            restype, _ = ic.select(mailbox=mailbox)
            check_restype(restype, f'failed to SELECT mailbox {mailbox}')

            # First, query for *all* message UIDs in the selected mailbox.
            # Interpret the response as a list of integers.
            logger.debug('Getting UID list')
            restype, [uids] = ic.uid('SEARCH', 'ALL')
            check_restype(restype, 'failed to execute SEARCH')
            uids = [*map(int, filter(None, uids.split(b' ')))]

            # In the event that the mailbox is empty, there will be no UIDs and
            # nothing more to do.
            if not uids:
                logger.debug('No messages in this mailbox')
                raise NoMessages

            # Fetch a range of message headers, from the smallest UID to the
            # largest UID. Build a structure that links each UID to the `Date`
            # header on the message it refers to.
            message_set = f'{min(uids)}:{max(uids)}'
            logger.debug(f'Fetching headers in UID range {message_set}')
            restype, resdata = ic.uid('FETCH', message_set, '(BODY.PEEK[HEADER])')
            check_restype(restype, f'failed to execute FETCH UIDs {message_set} (peek)')
            uids_dated = self.date_uid_map(data=resdata)

            # Iterate over all UIDs in date order, oldest to newest.
            for _, uid in sorted(uids_dated, key=itemgetter(0)):
                # Fetch the full message content, wrap it in an IMAPMessage and
                # yield it to the caller.
                logger.debug(f'Fetching message UID {int(uid)}')
                restype, resdata = ic.uid('FETCH', uid, '(RFC822)')
                check_restype(restype, f'failed to execute FETCH UID {int(uid)} (full)')

                yield IMAPMessage(data=resdata, imap_connection=ic, uid=uid)


class IMAPMessage:
    """
    IMAP4 email message with basic multipart support.

    Each message is represented as a set of metadata attributes (generally
    corresponding to header values) and a mapping of MIME-types and lists
    containing each piece of multipart data matching that type. As an example,
    imagine an HTML email body with two inline images interleaved between three
    pieces of text content:

      text piece 1
      <image 1>
      text piece 2
      <image 2>
      text piece 3

    The IMAPMessage layout would be:

    IMAPMessage:
      - (headers...)
      - text/html: [
        - text piece 1
        - text piece 2
        - text piece 3
      ]
      - image/jpeg: [
        - image bytes 1
        - image bytes 2
      ]

      Note that this destroys the ordering relationships between inline
      attachments and the text that surrounds them. This is very much by design;
      Windowbox doesn't need to preserve that for its purposes.
    """

    def __init__(self, *, data, imap_connection, uid):
        """
        Constructor.

        Args:
            data: Raw response data from an IMAP FETCH command.
            imap_connection: A reference to the IMAP4 connection to the mailbox.
            uid: The IMAP4 UID of the current email message.
        """

        # Handle ugly IMAP FETCH structure and parse into an email object. This
        # should only be given single messages; the list unpack doesn't fail
        # when used correctly.
        [data] = (chunk[1] for chunk in data if isinstance(chunk, tuple))
        msg = email.message_from_bytes(data, policy=email.policy.SMTP)

        self.imap_connection = imap_connection
        self.uid = uid
        self.date = email.utils.parsedate_to_datetime(msg['date'])
        self.from_name, self.from_address = email.utils.parseaddr(msg['from'])
        self.message_id = msg['message-id']
        self.x_mailer = msg['x-mailer']
        self.parts_by_type = defaultdict(list)

        for part in msg.walk():
            # Only want to process parts that do not contain sub-parts
            if part.is_multipart():
                continue

            # Read content and, if it's text, normalize newlines.
            content = part.get_content()
            if isinstance(content, str):
                while '\r\n' in content:
                    content = content.replace('\r\n', '\n')

            # Store this content part
            mime_type = part.get_content_type()
            self.parts_by_type[mime_type].append(content)

    @property
    def part_types(self):
        """
        Get all MIME-types present in this message.

        Returns:
            All MIME-types present in this message, in no meaningful order.
        """
        return set(self.parts_by_type)

    @property
    def text_plain(self):
        """
        Get the concatenation of all plain-text parts of the message.

        Returns:
            Text content, or an empty string if none is present.
        """
        return ''.join(self.parts_by_type['text/plain'])

    def delete(self):
        """
        Delete (from the IMAP server) the message that this instance represents.

        In Gmail terms, this moves the message out of the Inbox and into All
        Mail. (It would require another flag operation to then move it to Trash,
        which would somewhat limit portability.) After the flagging is done, the
        mailbox is automatically EXPUNGE'd.
        """
        logger.debug(f'Setting delete flag on UID {int(self.uid)}')
        restype, _ = self.imap_connection.uid('STORE', self.uid, '+FLAGS', '\\Deleted')
        check_restype(restype, f'failed to flag UID {int(self.uid)} as deleted')

        logger.debug('Expunging')
        restype, _ = self.imap_connection.expunge()
        check_restype(restype, 'failed to EXPUNGE')

    def yield_parts(self, mime_type):
        """
        Yield each defined part for the specified `mime_type`.

        Yields:
            Once per part. There may be zero, one, or many parts for a given
            MIME-type.
        """
        yield from self.parts_by_type[mime_type]
