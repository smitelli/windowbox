import json
import os
from PIL import Image as PILImage
from StringIO import StringIO
import subprocess
import sqlalchemy as sa
import windowbox.configs.base as cfg
from windowbox.database import (
    DeclarativeBase, JSONEncodedDict, session as db_session)
from windowbox.models import BaseModel, BaseFSEntity


class ImageManager():
    def get_image_by_post_id(self, post_id):
        return db_session.query(Image).filter(Image.post_id == post_id).first()


class ImageSchema(DeclarativeBase):
    __tablename__ = 'images'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id'))
    mime_type = sa.Column(sa.String(255))
    exif_data = sa.Column(JSONEncodedDict)


class Image(ImageSchema, BaseModel, BaseFSEntity):
    storage_path = os.path.join(cfg.STORAGE_DIR, 'original')
    mime_extension_map = {
        'image/gif': '.gif',
        'image/jpeg': '.jpg',
        'image/png': '.png'}

    def __repr__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)

    def set_data(self, *args, **kwargs):
        super(Image, self).set_data(*args, **kwargs)

        self.exif_data = self._load_exif_data()

    def get_derivative(self, width=None, height=None):
        derivative = db_session.query(ImageDerivative).filter(
            ImageDerivative.image_id == self.id, ImageDerivative.width == width, ImageDerivative.height == height).first()

        if not derivative:
            derivative = ImageDerivative(image_id=self.id, width=width, height=height)
            derivative.rebuild(source=self)

        if not os.path.isfile(derivative.get_file_name()):
            derivative.rebuild(source=self)

        return derivative

    def _load_exif_data(self):
        # Ask ExifTool to read file info, then convert it to a dict
        args = [cfg.EXIFTOOL, '-json', '-long', '-g', self.get_file_name()]
        json_data = subprocess.check_output(args)
        dict_data = json.loads(json_data)[0]

        # The following bits of data are not useful; they will be stripped
        bad_groups = ['ExifTool', 'SourceFile']
        bad_keys = [
            ('Composite', 'ThumbnailImage'),
            ('EXIF', 'ThumbnailLength'),
            ('EXIF', 'ThumbnailOffset'),
            ('File', 'Directory'),
            ('File', 'FileAccessDate'),
            ('File', 'FileInodeChangeDate'),
            ('File', 'FileModifyDate'),
            ('File', 'FileName'),
            ('File', 'FilePermissions'),
            ('File', 'MIMEType'),
            ('JFIF', 'ThumbnailImage')]

        for group in bad_groups:
            if group in dict_data:
                del dict_data[group]

        for group, key in bad_keys:
            if group in dict_data and key in dict_data[group]:
                del dict_data[group][key]

        return dict_data


class ImageDerivativeSchema(DeclarativeBase):
    __tablename__ = 'image_derivatives'
    __table_args__ = (sa.Index('image_id_and_dimensions', 'image_id', 'width', 'height'), )
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    image_id = sa.Column(sa.Integer, sa.ForeignKey('images.id'))
    width = sa.Column(sa.Integer, nullable=True)
    height = sa.Column(sa.Integer, nullable=True)
    mime_type = sa.Column(sa.String(255))


class ImageDerivative(ImageDerivativeSchema, BaseModel, BaseFSEntity):
    storage_path = os.path.join(cfg.STORAGE_DIR, 'derivative')
    mime_extension_map = Image.mime_extension_map

    def __repr__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)

    def rebuild(self, source):
        self.mime_type = source.mime_type
        im = PILImage.open(source.get_file_name())

        exif = source.exif_data
        try:
            orient_code = exif['EXIF']['Orientation']['num']
            im = self._transpose_derivative(im, orient_code)
        except KeyError:
            pass

        im = self._resize_derivative(im, self.width, self.height)

        self.save(commit=True)
        self._save_derivative(im)

    def _transpose_derivative(self, im, orient_code):
        operations = {
            1: (None, None),  # no rotation
            2: (None, PILImage.FLIP_LEFT_RIGHT),  # no rotation - horizontal flip
            3: (PILImage.ROTATE_180, None),  # 180deg rotate left
            4: (PILImage.ROTATE_180, PILImage.FLIP_LEFT_RIGHT),  # 180deg rotate left - horizontal flip
            5: (PILImage.ROTATE_270, PILImage.FLIP_LEFT_RIGHT),  # 90deg rotate right - horizontal flip
            6: (PILImage.ROTATE_270, None),  # 90deg rotate right
            7: (PILImage.ROTATE_90, PILImage.FLIP_LEFT_RIGHT),  # 90deg rotate left - horizontal flip
            8: (PILImage.ROTATE_90, None)}  # 90deg rotate left

        try:
            rotate, flip = operations[orient_code]
        except KeyError:
            return im

        if rotate:
            im = im.transpose(rotate)

        if flip:
            im = im.transpose(flip)

        return im

    def _resize_derivative(self, im, width, height):
        im = im.convert('RGB')

        old_width, old_height = im.size

        if width > 0 and height > 0:
            fx = float(old_width) / width
            fy = float(old_height) / height
            f = fx if fx < fy else fy
            crop_size = int(width * f), int(height * f)

            crop_width, crop_height = crop_size
            trim_x = (old_width - crop_width) / 2
            trim_y = (old_height - crop_height) / 2

            crop = trim_x, trim_y, crop_width + trim_x, crop_height + trim_y
            im = im.transform(crop_size, PILImage.EXTENT, crop)

            size = width, height

        elif width > 0 and height is None:
            f = float(old_width) / width
            size = width, int(old_height / f)

        elif height > 0 and width is None:
            f = float(old_height) / height
            size = int(old_width / f), height

        else:
            return im

        return im.resize(size, PILImage.ANTIALIAS)

    def _save_derivative(self, im):
        save_options = {
            'image/gif': {'format': 'GIF'},
            'image/jpeg': {'format': 'JPEG', 'quality': 95},
            'image/png': {'format': 'PNG', 'optimize': True}}

        io = StringIO()
        im.save(io, **save_options[self.mime_type])
        self.set_data(io.getvalue())
