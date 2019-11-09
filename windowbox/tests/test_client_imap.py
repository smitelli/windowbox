"""
Tests for the IMAP4 fetch client.
"""

import pytest
from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import Mock, call, patch
from windowbox.clients.imap import (
    IMAP_SSLClient, IMAPMessage, IMAPClientError, NoMessages)

HEADERS = [
    (
        b'1 (UID 1 BODY[HEADER] {100}',
        b'From: From Example <from@example.com>\r\n'
        b'Date: Sat, 28 Sep 2019 17:42:39 -0400\r\n'
        b'To: To Example <to@example.com>\r\n\r\n'
    ),
    b')',
    (
        b'2 (UID 2 BODY[HEADER] {100}',
        b'From: From Example <from@example.com>\r\n'
        b'Date: Wed, 30 Oct 2019 08:00:00 -0400\r\n'
        b'To: To Example <to@example.com>\r\n\r\n'
    ),
    b')',
    (
        b'3 (UID 3 BODY[HEADER] {100}',
        b'From: From Example <from@example.com>\r\n'
        b'Date: Wed, 01 Aug 2018 08:00:00 -0400\r\n'
        b'To: To Example <to@example.com>\r\n\r\n'
    ),
    b')']
HEADERS_JUNK = [
    (
        b'This is a bad UID line',
        b'This is not header data'
    ),
    b')']
HEADERS_NO_DATE = [
    (
        b'1 (UID 1 BODY[HEADER] {100}',
        b'From: From Example <from@example.com>\r\n'
        b'To: To Example <to@example.com>\r\n\r\n'
    ),
    b')']
FULL_MESSAGES = deepcopy(HEADERS)
FULL_MESSAGES[0] = (b'1 (UID 1 RFC822 {100}', FULL_MESSAGES[0][1] + b'Content for message UID 1')
FULL_MESSAGES[2] = (b'2 (UID 2 RFC822 {100}', FULL_MESSAGES[2][1] + b'Content for message UID 2')
FULL_MESSAGES[4] = (b'3 (UID 3 RFC822 {100}', FULL_MESSAGES[4][1] + b'Content for message UID 3')
COMPLEX_MESSAGE = [  # Message body copied from http://qcode.co.uk/post/70
    (
        b'1 (UID 1 BODY[HEADER] {100}',
        b'From: From Example <from@example.com>\r\n'
        b'Date: Sat, 28 Sep 2019 17:42:39 -0400\r\n'
        b'To: To Example <to@example.com>\r\n'
        b'Message-ID: <4d7158c6e3f347d799e2bfe6ede6f4d3@bar.baz>\r\n'
        b'X-Mailer: pytest and caffiene\r\n'
        b'Subject: Example Email\r\n'
        b'MIME-Version: 1.0\r\n'
        b'Content-Type: multipart/mixed; boundary="MixedBoundaryString"\r\n\r\n'
        b'--MixedBoundaryString\r\n'
        b'Content-Type: multipart/related; boundary="RelatedBoundaryString"\r\n\r\n'
        b'--RelatedBoundaryString\r\n'
        b'Content-Type: multipart/alternative; boundary="AlternativeBoundaryString"\r\n\r\n'
        b'--AlternativeBoundaryString\r\n'
        b'Content-Type: text/plain;charset="utf-8"\r\n'
        b'Content-Transfer-Encoding: quoted-printable\r\n\r\n'
        b'This is the plain text part of the email.\r\n'
        b'There are several lines.\r\n'
        b'I like adding them.\r\n\r\n'
        b'--AlternativeBoundaryString\r\n'
        b'Content-Type: text/html;charset="utf-8"\r\n'
        b'Content-Transfer-Encoding: quoted-printable\r\n\r\n'
        b'<html>\r\n'
        b'  <body>=0D\r\n'
        b'    <img src=3D=22cid:masthead.png=40qcode.co.uk=22 width=3D800 height=3D80>=0D\r\n'
        b'    <p>This is the html part of the email.</p>=0D\r\n'
        b'    <img src=3D=22cid:logo.png=40qcode.co.uk=22 width=3D200 height=3D60>=0D\r\n'
        b'  </body>=0D\r\n'
        b'</html>=0D\r\n\r\n'
        b'--AlternativeBoundaryString\r\n'
        b'Content-Type: text/plain;charset="utf-8"\r\n'
        b'Content-Transfer-Encoding: quoted-printable\r\n\r\n'
        b'In fact, I added another one like a weirdo.\r\n\r\n'
        b'--AlternativeBoundaryString--\r\n\r\n'
        b'--RelatedBoundaryString\r\n'
        b'Content-Type: image/jpeg;name="logo.png"\r\n'
        b'Content-Transfer-Encoding: base64\r\n'
        b'Content-Disposition: inline;filename="logo.png"\r\n'
        b'Content-ID: <logo.png@qcode.co.uk>\r\n\r\n'
        b'amtsb2hiaXVvbHJueXZzNXQ2XHVmdGd5d2VoYmFmaGpremxidTh2b2hydHVqd255aHVpbnRyZnhu\r\n'
        b'dWkgb2l1b3NydGhpdXRvZ2hqdWlyb2h5dWd0aXJlaHN1aWhndXNpaHhidnVqZmtkeG5qaG5iZ3Vy\r\n'
        b'a25qbW9nNXRwbF0nemVycHpvemlnc3k5aDZqcm9wdHo7amlodDhpOTA4N3U5Nnkwb2tqMm9sd3An\r\n'
        b'LGZ2cDBbZWRzcm85eWo1Zmtsc2xrZ3g=\r\n\r\n'
        b'--RelatedBoundaryString\r\n'
        b'Content-Type: image/jpeg;name="masthead.png"\r\n'
        b'Content-Transfer-Encoding: base64\r\n'
        b'Content-Disposition: inline;filename="masthead.png"\r\n'
        b'Content-ID: <masthead.png@qcode.co.uk>\r\n\r\n'
        b'aXR4ZGh5Yjd1OHk3MzQ4eXFndzhpYW9wO2tibHB6c2tqOTgwNXE0aW9qYWJ6aXBqOTBpcjl2MC1t\r\n'
        b'dGlmOTA0cW05dGkwbWk0OXQwYVttaXZvcnBhXGtsbGo7emt2c2pkZnI7Z2lwb2F1amdpNTh1NDlh\r\n'
        b'eXN6dWdoeXhiNzhuZzdnaHQ3eW9zemlqb2FqZWt0cmZ1eXZnamhka3JmdDg3aXV2dWd5aGVidXdz\r\n'
        b'dhyuhehe76YTGSFGA=\r\n\r\n'
        b'--RelatedBoundaryString--\r\n\r\n'
        b'--MixedBoundaryString\r\n'
        b'Content-Type: application/pdf;name="Invoice_1.pdf"\r\n'
        b'Content-Transfer-Encoding: base64\r\n'
        b'Content-Disposition: attachment;filename="Invoice_1.pdf"\r\n\r\n'
        b'aGZqZGtsZ3poZHVpeWZoemd2dXNoamRibngganZodWpyYWRuIHVqO0hmSjtyRVVPIEZSO05SVURF\r\n'
        b'SEx1aWhudWpoZ3h1XGh1c2loZWRma25kamlsXHpodXZpZmhkcnVsaGpnZmtsaGVqZ2xod2plZmdq\r\n'
        b'a2psajY1ZWxqanNveHV5ZXJ3NTQzYXRnZnJhZXdhcmV0eXRia2xhanNueXVpNjRvNWllc3l1c2lw\r\n'
        b'dWg4NTA0\r\n'
        b'--MixedBoundaryString\r\n'
        b'Content-Type: application/pdf;name="SpecialOffer.pdf"\r\n'
        b'Content-Transfer-Encoding: base64\r\n'
        b'Content-Disposition: attachment;filename="SpecialOffer.pdf"\r\n\r\n'
        b'aXBvY21odWl0dnI1dWk4OXdzNHU5NTgwcDN3YTt1OTQwc3U4NTk1dTg0dTV5OGlncHE1dW4zOTgw\r\n'
        b'cS0zNHU4NTk0eWI4OTcwdjg5MHE4cHV0O3BvYTt6dWI7dWlvenZ1em9pdW51dDlvdTg5YnE4N3Z3\r\n'
        b'OTViOHk5cDV3dTh5bnB3dWZ2OHQ5dTh2cHVpO2p2Ymd1eTg5MGg3ajY4bjZ2ODl1ZGlvcjQ1amts\r\n'
        b'dfnhgjdfihn=\r\n\r\n'
        b'--MixedBoundaryString--'
    ),
    b')']


@pytest.fixture
def imap_client():
    """
    Return an IMAP fetch client.
    """
    return IMAP_SSLClient(
        host='example.org',
        user='windowbox@example.org',
        password='hunter2')


@pytest.fixture
def imap_message():
    """
    Return an IMAP message instance.
    """
    return IMAPMessage(
        data=COMPLEX_MESSAGE,
        imap_connection=Mock(),
        uid=b'1')


def test_imapclient_constructor(imap_client):
    """
    Should correctly store all arguments and defaults.
    """
    assert imap_client.host == 'example.org'
    assert imap_client.port == 993
    assert imap_client.user == 'windowbox@example.org'
    assert imap_client.password == 'hunter2'

    # Once more, with explicit port override
    imap_client = IMAP_SSLClient(
        host='example.org',
        port=333,
        user='windowbox@example.org',
        password='hunter2')
    assert imap_client.host == 'example.org'
    assert imap_client.port == 333
    assert imap_client.user == 'windowbox@example.org'
    assert imap_client.password == 'hunter2'


def test_imapclient_date_uid_map(imap_client):
    """
    Should be able to parse IMAP headers and extract a date/UID pairing.
    """
    assert [*imap_client.date_uid_map(HEADERS)] == [
        (datetime(2019, 9, 28, 21, 42, 39, tzinfo=timezone.utc), b'1'),
        (datetime(2019, 10, 30, 12, 0, 0, tzinfo=timezone.utc), b'2'),
        (datetime(2018, 8, 1, 12, 0, 0, tzinfo=timezone.utc), b'3')]

    with pytest.raises(IMAPClientError, match='could not find a date header'):
        [*imap_client.date_uid_map(HEADERS_NO_DATE)]

    with pytest.raises(IMAPClientError, match='could not find a UID'):
        [*imap_client.date_uid_map(HEADERS_JUNK)]


def test_imapclient_yield_messages(imap_client):
    """
    Verify happy path of IMAP mailbox scraping.
    """
    mock_ic = Mock()
    mock_ic.login.return_value = ('OK', [b'test@example.com authenticated (Success)'])
    mock_ic.select.return_value = ('OK', [b'3'])
    mock_ic.uid.side_effect = [
        # Return value for ic.uid('SEARCH', 'ALL')
        ('OK', [b'1 2 3']),
        # ...for uid('FETCH', uids '(BODY.PEEK[HEADER])')
        ('OK', HEADERS),
        # ...for three iterations of ic.uid('FETCH', uid '(RFC822)')
        ('OK', FULL_MESSAGES[0:2]),
        ('OK', FULL_MESSAGES[2:4]),
        ('OK', FULL_MESSAGES[4:6])]

    with patch('imaplib.IMAP4_SSL') as mock_imap:
        mock_imap.return_value.__enter__.return_value = mock_ic

        messages = [*imap_client.yield_messages(mailbox='foobar')]

        # Should be three messages, ordered by Date header (old to new)
        assert len(messages) == 3
        assert messages[0].uid == b'3'
        assert messages[1].uid == b'1'
        assert messages[2].uid == b'2'

    mock_ic.login.assert_called_with(user='windowbox@example.org', password='hunter2')
    mock_ic.select.assert_called_with(mailbox='foobar')
    mock_ic.uid.assert_has_calls([
        call('SEARCH', 'ALL'),
        call('FETCH', '1:3', '(BODY.PEEK[HEADER])'),
        call('FETCH', b'3', '(RFC822)'),
        call('FETCH', b'1', '(RFC822)'),
        call('FETCH', b'2', '(RFC822)')])


def test_imapclient_yield_messages_empty(imap_client):
    """
    Should raise relatively early if there are no messages in the mailbox.
    """
    mock_ic = Mock()
    mock_ic.login.return_value = ('OK', [b'test@example.com authenticated (Success)'])
    mock_ic.select.return_value = ('OK', [b'0'])
    mock_ic.uid.return_value = ('OK', [b''])

    with patch('imaplib.IMAP4_SSL') as mock_imap:
        mock_imap.return_value.__enter__.return_value = mock_ic

        with pytest.raises(NoMessages):
            [*imap_client.yield_messages()]


def test_imapclient_yield_messages_errors(imap_client):
    """
    Should raise if errors are encountered at any point in the IMAP session.
    """
    mock_ic = Mock()
    mock_ic.login.return_value = ('OK', [b'test@example.com authenticated (Success)'])
    mock_ic.select.return_value = ('OK', [b'3'])
    mock_ic.uid.side_effect = [
        # Return value for ic.uid('SEARCH', 'ALL')
        ('OK', [b'1 2 3']),
        # ...for uid('FETCH', uids '(BODY.PEEK[HEADER])')
        ('OK', HEADERS),
        # ...for one bad iteration of ic.uid('FETCH', uid '(RFC822)')
        ('BAD', [b'Bad fetch'])]

    with patch('imaplib.IMAP4_SSL') as mock_imap:
        mock_imap.return_value.__enter__.return_value = mock_ic

        with pytest.raises(IMAPClientError, match=r'failed to execute FETCH UID 3 \(full\)'):
            [*imap_client.yield_messages()]

        mock_ic.uid.side_effect = [
            ('OK', [b'1 2 3']),
            ('BAD', [b'Bad peek'])]
        mock_ic.uid.reset_mock()

        with pytest.raises(IMAPClientError, match=r'failed to execute FETCH UIDs 1:3 \(peek\)'):
            [*imap_client.yield_messages()]

        mock_ic.uid.side_effect = [('BAD', [b'Bad search'])]
        mock_ic.uid.reset_mock()

        with pytest.raises(IMAPClientError, match='failed to execute SEARCH'):
            [*imap_client.yield_messages()]

        mock_ic.select.return_value = ('BAD', [b'Bad select'])

        with pytest.raises(IMAPClientError, match='failed to SELECT mailbox INBOX'):
            [*imap_client.yield_messages()]

        mock_ic.login.return_value = ('BAD', [b'Bad login'])

        with pytest.raises(IMAPClientError, match='failed to LOGIN as windowbox@example.org'):
            [*imap_client.yield_messages()]


def test_imapmessage_constructor(imap_message):
    """
    Verify construction of an IMAP message instance.
    """
    assert isinstance(imap_message.imap_connection, Mock)
    assert imap_message.uid == b'1'
    assert imap_message.date == datetime(2019, 9, 28, 21, 42, 39, tzinfo=timezone.utc)
    assert imap_message.from_name == 'From Example'
    assert imap_message.message_id == '<4d7158c6e3f347d799e2bfe6ede6f4d3@bar.baz>'
    assert imap_message.x_mailer == 'pytest and caffiene'

    assert len(imap_message.parts_by_type) == 4
    assert len(imap_message.parts_by_type['text/plain']) == 2
    assert len(imap_message.parts_by_type['text/html']) == 1
    assert len(imap_message.parts_by_type['image/jpeg']) == 2
    assert len(imap_message.parts_by_type['application/pdf']) == 2

    # Test text part specifically to verify \r was removed
    assert '\r' not in imap_message.parts_by_type['text/plain'][0]
    assert '\r' not in imap_message.parts_by_type['text/html'][0]


def test_imapmessage_part_types(imap_message):
    """
    Should return the set of all defined part types.
    """
    assert imap_message.part_types == {
        'text/plain', 'text/html', 'image/jpeg', 'application/pdf'}


def test_imapmessage_text_plain(imap_message):
    """
    Should be able to return a concatenation of all plaintext parts.
    """
    assert imap_message.text_plain == (
        '''This is the plain text part of the email.
There are several lines.
I like adding them.
In fact, I added another one like a weirdo.
''')


def test_imapmessage_delete(imap_message):
    """
    Should be able to issue a delete/EXPUNGE to the attached IMAP client.
    """
    mock_ic = imap_message.imap_connection
    mock_ic.uid.return_value = ('OK', [b''])
    mock_ic.expunge.return_value = ('OK', [b''])

    imap_message.delete()

    mock_ic.uid.assert_called_with('STORE', b'1', '+FLAGS', '\\Deleted')
    mock_ic.expunge.assert_called_with()

    # Test EXPUNGE failure
    mock_ic.expunge.return_value = ('BAD', [b''])
    with pytest.raises(IMAPClientError, match='failed to EXPUNGE'):
        imap_message.delete()

    # Test STORE failure
    mock_ic.uid.return_value = ('BAD', [b''])
    with pytest.raises(IMAPClientError, match='failed to flag UID 1 as deleted'):
        imap_message.delete()


def test_imapmessage_yield_parts(imap_message):
    """
    Should be able to yield each part of a message.
    """
    assert len([*imap_message.yield_parts('text/plain')]) == 2
    assert len([*imap_message.yield_parts('text/html')]) == 1
    assert len([*imap_message.yield_parts('image/jpeg')]) == 2
    assert len([*imap_message.yield_parts('application/pdf')]) == 2
