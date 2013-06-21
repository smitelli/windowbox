import os
from PIL import Image
from re import match
from StringIO import StringIO
import windowbox.configs.base as cfg
from windowbox.database import session as db_session
from windowbox.models import ImageOriginalSchema, ImageDerivativeSchema, BaseModel, BaseFSEntity


class ImageFactory():
    def get_original_by_id(self, post_id):
        return db_session.query(ImageOriginal).filter(ImageOriginal.post_id == post_id).first()

    def get_derivative(self, post_id, size):
        width, height = ImageDerivative.get_dimensions(size)
        clean_size = '{}x{}'.format(width, height)

        derivative = db_session.query(ImageDerivative).filter(
            ImageDerivative.post_id == post_id, ImageDerivative.size == clean_size).first()

        if not derivative:
            derivative = ImageDerivative(post_id=post_id, size=clean_size)
            derivative.rebuild()

        return derivative


class ImageOriginal(ImageOriginalSchema, BaseModel, BaseFSEntity):
    STORAGE_DIR = os.path.join(cfg.STORAGE_DIR, 'original')
    MIME_MAP = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif'}

    def __repr__(self):
        return '<ImageOriginal id={}>'.format(self.post_id)


class ImageDerivative(ImageDerivativeSchema, BaseModel, BaseFSEntity):
    STORAGE_DIR = os.path.join(cfg.STORAGE_DIR, 'derivatives')
    MIME_MAP = ImageOriginal.MIME_MAP

    def __repr__(self):
        return '<ImageDerivative id={} post_id={} size={}>'.format(
            self.derivative_id, self.post_id, self.size)

    def get_file_identifier(self):
        return str(self.derivative_id)

    @staticmethod
    def get_dimensions(size):
        matches = match('(\d*)x(\d*)', size or '')
        width, height = matches.groups() if matches else (0, 0)

        return (width or 0, height or 0)

    def rebuild(self):
        source = ImageFactory().get_original_by_id(self.post_id)

        self.mime_type = source.mime_type
        im = Image.open(source.get_file_name())

        #exif = self.get_exif_data(im)
        #if exif and 'Orientation' in exif:
        #    im = self._rotate_data(im, exif['Orientation'])

        width, height = self.get_dimensions(self.size)
        #im = self._resize_data(im, width, height)

        self.save(commit=True)
        self._save_derivative(im)

    def _save_derivative(self, image):
        io = StringIO()

        #if self.mime_type == 'image/png':
        #    image.save(io, 'PNG', optimize=True)
        #elif self.mime_type == 'image/gif':
        #    image.save(io, 'GIF')
        #else:
        #    image.save(io, 'JPEG', quality=95)
        image.save(io, 'JPEG', quality=95)

        self.set_data(io.getvalue())
