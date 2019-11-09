"""
Tests for the ExifTool client.
"""

import pytest
from unittest.mock import patch
from windowbox.clients.exiftool import ExifToolClient


@pytest.fixture
def exiftool():
    """
    Return an ExifTool client.
    """
    return ExifToolClient(exiftool_bin='/path/to/test/bin')


def test_constructor(exiftool):
    """
    Should accept and store all publicly-defined attributes.
    """
    assert exiftool.exiftool_bin == '/path/to/test/bin'


def test_read_file(exiftool):
    """
    Should invoke the exiftool binary and handle its output.
    """
    with patch('subprocess.check_output', return_value=b'[{"foo": "bar"}]') as mock_subprocess:
        assert exiftool.read_file('/path/to/test/image.jpg') == {'foo': 'bar'}
        mock_subprocess.assert_called_once_with([
            '/path/to/test/bin', '-binary', '-groupNames', '-json', '-long',
            '/path/to/test/image.jpg'])


def test_read_file_discard(exiftool):
    """
    Should discard all the patterns we don't care about.
    """
    retval = b'''[{
        "ExifTool:ExifToolVersion":{"desc":"ExifTool Version Number","val":11.16},
        "File:Directory":{"desc":"Directory","val":"/some"},
        "File:FileAccessDate":{"desc":"File Access Date/Time","val":"2019:10:26 03:22:44+00:00"},
        "File:FileInodeChangeDate":{"desc":"File Inode Change Date/Time","val":"2019:10:27 18:35:17+00:00"},
        "File:FileModifyDate":{"desc":"File Modification Date/Time","val":"2019:10:26 03:22:44+00:00"},
        "File:FileName":{"desc":"File Name","val":"image.png"},
        "File:FilePermissions":{"desc":"File Permissions","num":777,"val":"rwxrwxrwx"},
        "File:MIMEType":{"desc":"MIME Type","val":"image/png"},
        "SourceFile":"/some/image.png",
        "SomeThumbnailSomething":"junk",
        "OneGoodKey": "yup"
    }]'''

    with patch('subprocess.check_output', return_value=retval):
        assert exiftool.read_file('/path/to/test/image.jpg') == {'OneGoodKey': 'yup'}


def test_read_file_flatten(exiftool):
    """
    Should flatten any nested objects using a separator.
    """
    retval = b'''[{
        "scalar1": "scalar one",
        "scalar2": "scalar two",
        "object1": {
            "foo": "object one foo",
            "bar": "object one bar"
        },
        "object2": {
            "foo": "object two foo",
            "bar": "object two bar"
        },
        "nested1": {
            "foo": "nested one foo",
            "bar": "nested one bar",
            "nested2": {
                "foo": "nested two foo",
                "bar": "nested two bar",
                "nested3": {
                    "foo": "nested three foo",
                    "bar": "nested three bar"
                }
            }
        }
    }]'''

    with patch('subprocess.check_output', return_value=retval):
        assert exiftool.read_file('/path/to/test/image.jpg') == {
            'scalar1': 'scalar one',
            'scalar2': 'scalar two',
            'object1.foo': 'object one foo',
            'object1.bar': 'object one bar',
            'object2.foo': 'object two foo',
            'object2.bar': 'object two bar',
            'nested1.foo': 'nested one foo',
            'nested1.bar': 'nested one bar',
            'nested1.nested2.foo': 'nested two foo',
            'nested1.nested2.bar': 'nested two bar',
            'nested1.nested2.nested3.foo': 'nested three foo',
            'nested1.nested2.nested3.bar': 'nested three bar'}
