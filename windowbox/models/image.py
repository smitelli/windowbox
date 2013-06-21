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

        if not os.path.isfile(derivative.get_file_name()):
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

    @staticmethod
    def get_dimensions(size):
        matches = match('(\d*)x(\d*)', size or '')
        width, height = matches.groups() if matches else (0, 0)

        return (int(width or 0), int(height or 0))

    def rebuild(self):
        source = ImageFactory().get_original_by_id(self.post_id)

        self.mime_type = source.mime_type
        im = Image.open(source.get_file_name())

        # TODO
        #exif = self.get_exif_data(im)
        #if exif and 'Orientation' in exif:
        #    im = self._transpose_derivative(im, exif['Orientation'])

        width, height = self.get_dimensions(self.size)
        im = self._resize_derivative(im, width, height)

        self.save(commit=True)
        self._save_derivative(im)

    def _resize_derivative(self, im, width, height):
        old_width, old_height = im.size

        if width and height:
            fx = float(old_width) / width
            fy = float(old_height) / height
            f = fx if fx < fy else fy
            crop_size = int(width * f), int(height * f)

            crop_width, crop_height = crop_size
            trim_x = (old_width - crop_width) / 2
            trim_y = (old_height - crop_height) / 2

            crop = trim_x, trim_y, crop_width + trim_x, crop_height + trim_y
            im = im.transform(crop_size, Image.EXTENT, crop)

            size = width, height

        elif width and not height:
            f = float(old_width) / width
            size = width, int(old_height / f)

        elif height and not width:
            f = float(old_height) / height
            size = int(old_width / f), height

        else:
            return im

        return im.resize(size, Image.ANTIALIAS)

    def _transpose_derivative(self, im, orient_code):
        operations = {
            1: (None, None),  # no rotation
            2: (None, Image.FLIP_LEFT_RIGHT),  # no rotation - horizontal flip
            3: (Image.ROTATE_180, None),  # 180deg rotate left
            4: (Image.ROTATE_180, Image.FLIP_LEFT_RIGHT),  # 180deg rotate left - horizontal flip
            5: (Image.ROTATE_270, Image.FLIP_LEFT_RIGHT),  # 90deg rotate right - horizontal flip
            6: (Image.ROTATE_270, None),  # 90deg rotate right
            7: (Image.ROTATE_90, Image.FLIP_LEFT_RIGHT),  # 90deg rotate left - horizontal flip
            8: (Image.ROTATE_90, None)  # 90deg rotate left
        }

        try:
            rotate, flip = operations[orient_code]
        except KeyError:
            return im

        if rotate:
            im = im.transpose(rotate)

        if flip:
            im = im.transpose(flip)

        return im

    def _save_derivative(self, im):
        io = StringIO()

        # TODO
        #if self.mime_type == 'image/png':
        #    image.save(io, 'PNG', optimize=True)
        #elif self.mime_type == 'image/gif':
        #    image.save(io, 'GIF')
        #else:
        #    image.save(io, 'JPEG', quality=95)
        im.save(io, 'JPEG', quality=95)

        self.set_data(io.getvalue())
