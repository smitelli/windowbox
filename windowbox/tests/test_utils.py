"""
Tests for the app utilities.
"""

import pytest
import windowbox.utils
from datetime import datetime, timezone


def test_datetime_to_rfc2822():
    """
    Should be able to convert a datetime into an RFC 2822 date string.
    """
    dt = datetime(2019, 10, 27, 18, 20, 0, tzinfo=timezone.utc)
    assert windowbox.utils.datetime_to_rfc2822(dt) == 'Sun, 27 Oct 2019 18:20:00 +0000'


def test_minify_html():
    """
    Should correctly minify HTML content.

    This test is checking for:
      - Reduced whitespace and newlines
      - Boolean attributes losing the ="value"
      - Quotes on other attributes remaining
    """
    html = '''
        <div>
            <p>
                <input checked="true">
                <a name="attr">
                    <h1>Significant Whitespace</h1>
                </a>
            </p>
        </div>
        '''

    assert windowbox.utils.minify_html(html) == \
        '<div><p><input checked><a name="attr"><h1>Significant Whitespace</h1></a></p></div>'


def test_minify_xml():
    """
    Should correctly minify XML content.

    This test is checking for:
      - Reduced whitespace and newlines
      - Insertion of an XML declaration with the provided encoding
    """
    xml = '''
        <top>
            <el>
                <data>first</data>
            </el>
            <el>
                <data>second</data>
            </el>
        </top>
        '''

    assert windowbox.utils.minify_xml(xml, encoding='utf-8') == \
        b"<?xml version='1.0' encoding='utf-8'?>\n" \
        b"<top><el><data>first</data></el><el><data>second</data></el></top>"


def test_truncate_text():
    """
    Should correctly truncate text to arbitrary lengths.
    """
    trunc = windowbox.utils.truncate_text
    message = 'Sphinx of black quartz, judge my vow.'

    assert trunc(message, 1, suffix='') == 'S'
    assert trunc(message, 4) == 'S...'
    assert trunc(message, 8) == 'Sphin...'
    assert trunc(message, 9) == 'Sphinx...'
    assert trunc(message, 11) == 'Sphinx...'
    assert trunc(message, 12) == 'Sphinx of...'
    assert trunc(message, 17) == 'Sphinx of...'
    assert trunc(message, 18) == 'Sphinx of black...'
    assert trunc(message, 25) == 'Sphinx of black...'
    assert trunc(message, 26) == 'Sphinx of black quartz,...'
    assert trunc(message, 36) == 'Sphinx of black quartz, judge my...'
    assert trunc(message, 37) == 'Sphinx of black quartz, judge my vow.'
    assert trunc(message, 100) == 'Sphinx of black quartz, judge my vow.'

    # This would result in "..."
    with pytest.raises(ValueError, match='not enough room for any text'):
        trunc(message, 3)
