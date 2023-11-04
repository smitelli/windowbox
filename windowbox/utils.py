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
