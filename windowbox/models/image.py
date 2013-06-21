import errno
import os
from windowbox.configs.base import STORAGE_DIR
from windowbox.database import session as db_session
from windowbox.models import ImageOriginalSchema, BaseModel
from windowbox.utils import id_to_directory


class ImageFactory():
    def get_original_by_id(self, post_id):
        return db_session.query(ImageOriginal).filter(ImageOriginal.post_id == post_id).first()


class ImageOriginal(ImageOriginalSchema, BaseModel):
    def __repr__(self):
        return '<ImageOriginal id={}>'.format(self.post_id)

    def get_data(self):
        with open(self.get_file_name(), mode='rb') as fh:
            image_data = fh.read()

        return image_data

    def set_data(self, image_data):
        file_name = self.get_file_name()
        path = os.path.dirname(file_name)

        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

        with open(file_name, mode='wb') as fh:
            fh.write(image_data)

    def set_data_from_file(self, file_name):
        with open(file_name, mode='rb') as fh:
            image_data = fh.read()

        self.set_data(image_data)

    def get_file_name(self):
        storage_dir = os.path.join(STORAGE_DIR, 'original')
        d1, d2 = id_to_directory(self.post_id)
        file_name = '{}{}'.format(self.post_id, self.get_extension())

        return os.path.join(storage_dir, d1, d2, file_name)

    def get_extension(self):
        mime_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif'}

        try:
            return mime_map[self.mime_type]
        except KeyError:
            return ''
