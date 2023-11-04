"""
Tests for the app utilities.
"""

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
