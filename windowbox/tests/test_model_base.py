"""
Tests for the base model mixins.
"""

import io
import pytest
from unittest.mock import Mock, patch
from windowbox.models import FilesystemMixin


@pytest.fixture
def fs_tester(tmp_path):
    """
    Return a tester stub with a valid (and ephemeral) base path and ID.
    """
    class FS_Tester(FilesystemMixin):
        def __init__(self, base_path, id, mime_type):
            self.base_path = base_path
            self.id = id
            self.mime_type = mime_type

    yield FS_Tester(base_path=tmp_path, id=1234, mime_type='image/jpeg')


def test_fs_mixin_has_storage_data(tmp_path, fs_tester):
    """
    Should be able to discern if storage data is present on disk.
    """
    storage_path = tmp_path / 'storage.data'

    with patch('windowbox.models.FilesystemMixin.storage_path', return_value=storage_path):
        try:
            storage_path.unlink()
        except FileNotFoundError:
            pass
        assert not fs_tester.has_storage_data

        storage_path.touch()
        assert fs_tester.has_storage_data


def test_fs_mixin_storage_data_size_bytes(tmp_path, fs_tester):
    """
    Should be able to measure the size of the storage data.
    """
    storage_path = tmp_path / 'storage.data'
    storage_path.write_bytes(b'\x00' * 50)

    with patch('windowbox.models.FilesystemMixin.storage_path', return_value=storage_path):
        assert fs_tester.storage_data_size_bytes == 50


def test_fs_mixin_storage_path_requirements(fs_tester):
    """
    Should require needed instance attributes to be set.
    """

    # It should require base_path
    old_base_path = fs_tester.base_path
    fs_tester.base_path = None
    with pytest.raises(RuntimeError, match='base_path should not be None'):
        fs_tester.storage_path()
    fs_tester.base_path = old_base_path

    # It should require id
    old_id = fs_tester.id
    fs_tester.id = None
    with pytest.raises(RuntimeError, match='id should not be None'):
        fs_tester.storage_path()
    fs_tester.id = old_id


def test_fs_mixin_storage_path_directory(fs_tester):
    """
    Should construct a directory prefix using the first digits of the ID.
    """

    # Before mucking with IDs, verify the directory gets created if requested
    fs_tester.storage_path()
    assert not (fs_tester.base_path / '1' / '2').is_dir()
    fs_tester.storage_path(create_parents=True)
    assert (fs_tester.base_path / '1' / '2').is_dir()

    prefix = str(fs_tester.base_path)

    # One-digit IDs...
    for i in range(10):
        fs_tester.id = i
        assert str(fs_tester.storage_path()).startswith(f'{prefix}/0/0/')

    # Two-digit IDs...
    for i in range(10, 100, 10):
        fs_tester.id = i
        assert str(fs_tester.storage_path()).startswith(f'{prefix}/0/{i // 10}/')

    # Three-digit IDs...
    for i in range(100, 1000, 10):
        fs_tester.id = i
        assert str(fs_tester.storage_path()).startswith(f'{prefix}/{i // 100}/{(i // 10) % 10}/')

    # Spot-check a few bigger IDs since the loop-based approach falls apart
    fs_tester.id = 1234
    assert str(fs_tester.storage_path()).startswith(f'{prefix}/1/2/')
    fs_tester.id = 23456
    assert str(fs_tester.storage_path()).startswith(f'{prefix}/2/3/')
    fs_tester.id = 345678
    assert str(fs_tester.storage_path()).startswith(f'{prefix}/3/4/')
    fs_tester.id = 4567890
    assert str(fs_tester.storage_path()).startswith(f'{prefix}/4/5/')


def test_fs_mixin_set_storage_data(fs_tester):
    """
    Should be able to save a bunch of bytes.
    """
    fs_tester.set_storage_data(b'SNAUSAGES')

    assert (fs_tester.base_path / '1' / '2' / '1234.jpg').read_bytes() == b'SNAUSAGES'


def test_fs_mixin_set_storage_data_from_image(fs_tester):
    """
    Should be able to save data from a PIL Image.
    """
    fake_image = Mock()

    fs_tester.mime_type = 'image/jpeg'
    fs_tester.set_storage_data_from_image(fake_image)

    args, kwargs = fake_image.save.call_args
    assert str(kwargs['fp']).endswith('/1234.jpg')
    assert kwargs['optimize'] is True
    assert kwargs['quality'] == 75
    assert kwargs['progressive'] is True
    assert kwargs['subsampling'] == '4:4:4'

    fs_tester.mime_type = 'image/png'
    fs_tester.set_storage_data_from_image(fake_image)

    args, kwargs = fake_image.save.call_args
    assert str(kwargs['fp']).endswith('/1234.png')
    assert kwargs['optimize'] is True


def test_fs_mixin_get_storage_data_as_image(fs_tester, png_pixel):
    """
    Should be able to read the storage data and return a PIL Image.
    """
    png_fh = io.BytesIO(png_pixel)

    fs_tester.storage_path = Mock(return_value=png_fh)

    image = fs_tester.get_storage_data_as_image()
    assert image.size == (1, 1)
    assert image.convert('RGB').load()[0, 0] == (255, 0, 0)
