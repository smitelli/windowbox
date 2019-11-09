"""
Model utility functions and mixins.
"""

import mimetypes
from PIL import Image


def import_all_models():
    """
    Import all of the defined model modules so SQLAlchemy is aware of them.
    """
    import windowbox.models.attachment  # noqa: F401
    import windowbox.models.derivative  # noqa: F401
    import windowbox.models.post  # noqa: F401
    import windowbox.models.sender  # noqa: F401


class FilesystemMixin:
    """
    Adds filesystem storage capabilities to any model class.

    Classes that utilize this mixin need to implement the following attributes:
      - base_path
      - id
      - mime_type (optional; influences file extensions on disk)

    Attributes:
        FALLBACK_EXTENSION: If a fixed extension is not defined, and the MIME
            "guess extension" function failed to make a guess, this is the
            extension that will be used.
        KNOWN_EXTENSIONS: Mapping of MIME-types to file extensions. Anything
            defined here will be used unconditionally if found.
        IMAGE_SAVE_OPTIONS: Mapping of MIME-types to dictionaries, each one
            defining the options to pass to the Image.save() method when writing
            that type of image file.
        base_path: A pathlib Path object which refers to the root directory
            where all storage data should be located. Within this root, a two-
            level nested directory structure is used to keep the number of
            directory entries manageable.
    """

    FALLBACK_EXTENSION = '.dat'
    KNOWN_EXTENSIONS = {
        'image/jpeg': '.jpg',
        'image/png': '.png'}
    IMAGE_SAVE_OPTIONS = {
        'image/jpeg': {
            'quality': 75,
            'optimize': True,
            'progressive': True,
            'subsampling': '4:4:4'},
        'image/png': {
            'optimize': True}}

    base_path = None

    @property
    def has_storage_data(self):
        """
        Does this instance currently have data stored on the filesystem?

        Returns:
            Boolean True if a file exists at the storage path for this instance.
        """
        return self.storage_path().is_file()

    @property
    def storage_data_size_bytes(self):
        """
        How much space does the storage data for this instance use?

        Returns:
            File size in bytes.
        """
        return self.storage_path().stat().st_size

    def storage_path(self, *, create_parents=False):
        """
        Use the current state of the model to make a unique filesystem name.

        In all cases, uses `base_path` as the topmost directory. Note that for
        this to work correctly, the model instance must have its `id` and
        `mime_type` attributes set. For a newly-created instance with an auto-
        incrementing `id`, this usually requires the DB flush() method.

        Args:
            create_parents: If True, try to create all necessary parent
                directories before returning. This should be enabled during
                calls that intend to write to the path, and False during read.

        Returns:
            Complete base path plus the unique directory/file names that
            reference the file data. If `create_parents` was True, this file
            should be safe to write to.
        """
        if self.base_path is None:
            raise RuntimeError('base_path should not be None')

        if self.id is None:
            raise RuntimeError('id should not be None')

        id_str = str(self.id)

        if len(id_str) <= 1:
            d1, d2 = '0', '0'
        elif len(id_str) == 2:
            d1, d2 = '0', id_str[0]
        else:
            d1, d2 = id_str[0], id_str[1]

        prefix = self.base_path / d1 / d2
        if create_parents:
            prefix.mkdir(parents=True, exist_ok=True)

        extension = (
            self.KNOWN_EXTENSIONS.get(self.mime_type)
            or mimetypes.guess_extension(self.mime_type)
            or self.FALLBACK_EXTENSION)

        return prefix / f'{id_str}{extension}'

    def set_storage_data(self, data):
        """
        Convenience method to write to the storage path.

        Args:
            data: Data to write (bytes, in binary mode) to the storage path. The
                file will be created if it doesn't exist, or silently
                overwritten if it does exist.
        """
        self.storage_path(create_parents=True).write_bytes(data)

    def set_storage_data_from_image(self, image):
        """
        Write the contents of a PIL Image to the storage path.

        Args:
            image: Instance of a PIL Image.
        """
        save_options = self.IMAGE_SAVE_OPTIONS.get(self.mime_type, {})

        image.save(fp=self.storage_path(create_parents=True), **save_options)

    def get_storage_data_as_image(self):
        """
        Return the current storage path data as a PIL Image.

        The caller should know whether or not the underlying data is appropriate
        for reading as an image. No effort is made here to validate that.

        Returns:
            PIL Image object representing the storage path data.
        """
        return Image.open(self.storage_path())
