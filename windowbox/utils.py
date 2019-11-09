"""
Useful utilities and other odds-and-ends.
"""

import email.utils
from htmlmin import minify
from lxml import etree


def datetime_to_rfc2822(dt):
    """
    Return `dt` as an RFC 2822 date string.

    Args:
        dt: datetime object to format.

    Returns:
        String representation of the provided datetime in RFC 2822 format.
    """
    return email.utils.format_datetime(dt)


def minify_html(content):
    """
    Remove excess whitespace in an HTML string.

    Args:
        content: String containing any arbitrary HTML.

    Returns:
        Modified copy of the original content, which excess whitespace stripped.
    """
    return minify(
        input=content, remove_empty_space=True, reduce_boolean_attributes=True,
        remove_optional_attribute_quotes=False)


def minify_xml(content, *, encoding):
    """
    Remove excess whitespace in an XML string.

    Args:
        content: String containing any arbitrary XML.
        encoding: The character encoding to insert in the XML declaration.

    Returns:
        Modified copy of the original content, which excess whitespace stripped.
    """
    root = etree.XML(content, parser=etree.XMLParser(
        remove_blank_text=True, strip_cdata=False))

    return etree.tostring(root, encoding=encoding, xml_declaration=True)


def truncate_text(text, max_length, *, suffix='...'):
    """
    Truncate `text` to `max_length`, adding `suffix` if anything was removed.

    Performs no changes unless `text` is longer than `max_length`. If truncation
    is warranted, the length of the output *including the suffix* will be at or
    below `max_length`.

    Args:
        text: Text to possibly truncate.
        max_length: The absolute longest length allowed to be returned by this
            function.
        suffix: If the text was truncated, this will be appended to the end of
            the output to indicate it.

    Returns:
        String copy of `text`, truncated.
    """
    if len(text) <= max_length:
        return text

    max_length -= len(suffix)

    if max_length < 1:
        raise ValueError('not enough room for any text')

    if not text[max_length - 1].isspace() and not text[max_length].isspace():
        # Common case: The split boundary is in the middle of a word.
        keep = text[:max_length].rsplit(None, 1)[0]
    else:
        # Special case: The split boundary is already a word break.
        keep = text[:max_length].rstrip()

    return keep + suffix
