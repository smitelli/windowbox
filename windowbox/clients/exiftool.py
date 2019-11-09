"""
Wrapper client for the ExifTool binary.

Attributes:
    DISCARD_PATTERNS: List of compiled regex patterns which are used to weed out
        unwanted EXIF data from ever being returned by this client.
    FLATTEN_SEPARATOR: The character(s) to insert between key levels of a dict
        that has been run through flatten_dict().
    logger: Logger instance scoped to the current module name.
"""

import json
import logging
import re
import subprocess

DISCARD_PATTERNS = [
    re.compile(r'Thumbnail'),
    re.compile(r'^ExifTool'),
    re.compile(r'^File:Directory$'),
    re.compile(r'^File:FileAccessDate$'),
    re.compile(r'^File:FileInodeChangeDate$'),
    re.compile(r'^File:FileModifyDate$'),
    re.compile(r'^File:FileName$'),
    re.compile(r'^File:FilePermissions$'),
    re.compile(r'^File:MIMEType$'),
    re.compile(r'^SourceFile$')]
FLATTEN_SEPARATOR = '.'

logger = logging.getLogger(__name__)


def flatten_dict(src_dict, *, _prefix=''):
    """
    Flatten a nested dict by rewriting keys using dots.

    Given a source dictionary:

        {
            'first': '1st',
            'second': '2nd',
            'third': {'digit': 3, 'suffix': 'rd', 'split': 'yup!'},
            'fourth': {'meal': 'sure.'}
        }

    ...this generates a flattened copy:

        {
            'first': '1st',
            'second': '2nd',
            'third.digit': 3,
            'third.suffix': 'rd',
            'third.split': 'yup!',
            'fourth.meal': 'sure.'
        }

    The dot could be any character (or characters) defined through the
    FLATTEN_SEPARATOR attribute.

    Args:
        src_dict: The input dict to process.
        _prefix: Maintains the ancestor component(s) of the key during
            recursion. Not really intended for public use.

    Returns:
        New dict with the keyspace flattened.
    """
    dest_dict = {}

    for key, value in src_dict.items():
        if isinstance(value, dict):
            dest_dict.update(flatten_dict(value, _prefix=f'{_prefix}{key}{FLATTEN_SEPARATOR}'))
        else:
            dest_dict[f'{_prefix}{key}'] = value

    return dest_dict


class ExifToolClient:
    """
    Provides a simplified interface to run ExifTool and get output as a dict.

    NOTE: The discard patterns defined by this client are *not* meant to provide
    privacy and/or anonymity -- their intention is to avoid filling the database
    with irrelevant junk about the source filesystem and thumbnails. There WILL
    be private data returned by this client (GPS position, dates, times, camera
    metadata...) and no scrubbing/anonymization is performed.
    """

    def __init__(self, *, exiftool_bin):
        """
        Constructor.

        Args:
            exiftool_bin: Full path a suitable exiftool binary.
        """
        self.exiftool_bin = exiftool_bin

    def read_file(self, filename):
        """
        Read and return the EXIF data from the file at `filename`.

        Args:
            filename: The file to read. Can be any file that ExifTool knows how
                to read.

        Returns:
            Dict containing EXIF data. The keys are usually grouped in
            "Group:Item" format, and the values are themselves dicts with
            different structures depending on the underlying data.
        """
        args = [
            self.exiftool_bin, '-binary', '-groupNames', '-json', '-long',
            str(filename)]

        logger.debug(f'Executing {" ".join(args)}...')
        exif_json = subprocess.check_output(args)
        logger.debug(f'...got {len(exif_json)} bytes')

        exif_data = json.loads(exif_json)[0]

        for pattern in DISCARD_PATTERNS:
            exif_data = {k: v for k, v in exif_data.items() if not pattern.search(k)}

        return flatten_dict(exif_data)
