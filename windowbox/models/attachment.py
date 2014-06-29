from __future__ import absolute_import, division
import json
import os
import re
import subprocess
import requests
from StringIO import StringIO
from PIL import Image
from flask import current_app, url_for
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import column_mapped_collection
from windowbox.database import db
from windowbox.models import BaseFSEntity, BaseModel
from windowbox.models.metadata import Metadata


class AttachmentManager(object):
    @staticmethod
    def get_by_id(attachment_id):
        return Attachment.query.filter_by(id=attachment_id).first()

    @staticmethod
    def get_by_post_id(post_id):
        return Attachment.query.filter_by(post_id=post_id).first()

    @staticmethod
    def encode_dimensions(width=None, height=None, allow_crop=True):
        if not width and not height:
            return None
        else:
            combiner = 'x' if allow_crop else ':'

            return '{}{}{}'.format(width or '', combiner, height or '')

    @staticmethod
    def decode_dimensions(dimensions):
        matches = re.match('(?P<width>\d*)(?P<combiner>[x:])(?P<height>\d*)', dimensions)

        if not matches:
            return (None, None, True)

        def str_to_int(value):
            try:
                return int(value)
            except ValueError:
                return None

        width = str_to_int(matches.group('width'))
        height = str_to_int(matches.group('height'))
        allow_crop = (matches.group('combiner') == 'x')

        return (width, height, allow_crop)


class AttachmentAttribute(db.Model):
    __tablename__ = 'attachment_attributes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.id'))
    name = db.Column(db.String(64))
    value = db.Column(db.String(255))


class Attachment(db.Model, BaseModel, BaseFSEntity):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)
    mime_type = db.Column(db.String(255))
    geo_latitude = db.Column(db.Float, nullable=True)
    geo_longitude = db.Column(db.Float, nullable=True)
    geo_address = db.Column(db.Unicode(255), nullable=True)

    # Used to form the one-to-many relationship with AttachmentAttributes
    _attributes_dict = db.relationship(
        AttachmentAttribute,
        collection_class=column_mapped_collection(AttachmentAttribute.name))
    attributes = association_proxy(
        '_attributes_dict', 'value',
        creator=lambda n, v: AttachmentAttribute(name=n, value=v))

    MIME_EXTENSION_MAP = {
        'image/gif': '.gif',
        'image/jpeg': '.jpg',
        'image/png': '.png'}

    # The following bits of EXIF data are not useful; they will be stripped
    BAD_EXIF_KEY_PREFIXES = (
        'ExifTool',
        'SourceFile',
        'Composite.ThumbnailImage',
        'EXIF.ThumbnailLength',
        'EXIF.ThumbnailOffset',
        'File.Directory',
        'File.FileAccessDate',
        'File.FileInodeChangeDate',
        'File.FileModifyDate',
        'File.FileName',
        'File.FilePermissions',
        'File.MIMEType',
        'JFIF.ThumbnailImage')

    def __repr__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)

    def get_storage_path(self):
        return os.path.join(current_app.config['STORAGE_DIR'], 'attachments')

    def set_data(self, *args, **kwargs):
        super(Attachment, self).set_data(*args, **kwargs)

        self.attributes = self._load_exif_data()

        try:
            self.geo_latitude = float(self.attributes['Composite.GPSLatitude.num'])
            self.geo_longitude = float(self.attributes['Composite.GPSLongitude.num'])
            self.geo_address = self._load_address_data(self.geo_latitude, self.geo_longitude)
        except KeyError:
            current_app.logger.error('Could not get geo address for %d,%d', self.geo_latitude, self.geo_longitude)
            self.geo_latitude = None
            self.geo_longitude = None
            self.geo_address = None

    def get_metadata(self):
        return Metadata(self.attributes)

    def get_derivative(self, width=None, height=None, allow_crop=True):
        derivative = AttachmentDerivative.query.filter_by(
            attachment_id=self.id, width=width, height=height, allow_crop=allow_crop).first()

        if not derivative:
            current_app.logger.debug('Building new derivative')
            derivative = AttachmentDerivative(
                attachment_id=self.id, width=width, height=height, allow_crop=allow_crop)
            derivative.rebuild(source_attachment=self)
        elif not os.path.isfile(derivative.get_file_name()):
            current_app.logger.warn('Could not find derivative file; rebuilding')
            derivative.rebuild(source_attachment=self)

        return derivative

    def get_derivative_url(self, width=None, height=None, allow_crop=True, **kwargs):
        dimensions = AttachmentManager.encode_dimensions(width, height, allow_crop)

        kwargs.update({
            'attachment_id': self.id,
            'dimensions': dimensions})

        return url_for('get_attachment_derivative', **kwargs)

    def to_dict(self, lookup_children=False):
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'mime_type': self.mime_type,
            'geo_address': self.geo_address}

        if lookup_children:
            data['metadata'] = self.get_metadata().to_dict()

        return data

    def _load_exif_data(self):
        def flatten_dict(d):
            def expand(key, value):
                if isinstance(value, dict):
                    return [(key + '.' + k, v) for k, v in flatten_dict(value).items()]
                else:
                    return [(key, str(value))]
            return dict([item for k, v in d.items() for item in expand(k, v)])

        # Ask ExifTool to read file info, then convert it to a dict
        exiftool = current_app.config['EXIFTOOL']
        args = [exiftool, '-json', '-long', '-groupHeadings', self.get_file_name()]
        json_data = subprocess.check_output(args)
        dict_data = json.loads(json_data)[0]
        flat_data = flatten_dict(dict_data)

        for key in flat_data.keys():
            if key.startswith(self.BAD_EXIF_KEY_PREFIXES):
                del flat_data[key]

        return flat_data

    @staticmethod
    def _load_address_data(latitude, longitude, timeout=10):
        url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&sensor=true'.format(latitude, longitude)
        response = requests.get(url, timeout=timeout)
        if response.status_code is not requests.codes.ok:
            current_app.logger.debug('Maps API did not return HTTP OK')
            return None

        response_dict = response.json()
        if response_dict['status'] != 'OK':
            current_app.logger.debug('Maps API JSON did not contain OK status')
            return None

        for result in response_dict['results']:
            if result['geometry']['location_type'] != 'APPROXIMATE':
                continue
            return result['formatted_address']

        current_app.logger.debug('Maps API did not return any usable location types')
        return None


class AttachmentDerivative(db.Model, BaseModel, BaseFSEntity):
    __tablename__ = 'attachment_derivatives'
    __table_args__ = (db.Index(
        'attachment_id_dimensions', 'attachment_id', 'width', 'height', 'allow_crop', unique=True), )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.id'))
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    allow_crop = db.Column(db.Boolean)
    mime_type = db.Column(db.String(255))

    MIME_EXTENSION_MAP = Attachment.MIME_EXTENSION_MAP

    def __repr__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)

    def get_storage_path(self):
        return os.path.join(current_app.config['STORAGE_DIR'], 'derivatives')

    def rebuild(self, source_attachment):
        self.mime_type = source_attachment.mime_type
        im = Image.open(source_attachment.get_file_name())

        try:
            orient_code = int(source_attachment.attributes['EXIF.Orientation.num'])
        except (KeyError, ValueError):
            current_app.logger.debug('Image does not contain EXIF rotation data')
            orient_code = None

        if orient_code is not None:
            im = self._transpose_derivative(im, orient_code)

        im = self._resize_derivative(im, self.width, self.height, self.allow_crop)

        self._save_derivative(im)
        self.save(commit=True)

    @staticmethod
    def _transpose_derivative(im, orient_code):
        operations = {
            1: (None, None),  # no rotation
            2: (None, Image.FLIP_LEFT_RIGHT),  # no rotation - horizontal flip
            3: (Image.ROTATE_180, None),  # 180deg rotate left
            4: (Image.ROTATE_180, Image.FLIP_LEFT_RIGHT),  # 180deg rotate left - horizontal flip
            5: (Image.ROTATE_270, Image.FLIP_LEFT_RIGHT),  # 90deg rotate right - horizontal flip
            6: (Image.ROTATE_270, None),  # 90deg rotate right
            7: (Image.ROTATE_90, Image.FLIP_LEFT_RIGHT),  # 90deg rotate left - horizontal flip
            8: (Image.ROTATE_90, None)}  # 90deg rotate left

        try:
            rotate, flip = operations[orient_code]
        except KeyError:
            current_app.logger.debug('Orient code %d is out of range', orient_code)
            rotate = flip = None

        if rotate is not None:
            im = im.transpose(rotate)

        if flip is not None:
            im = im.transpose(flip)

        return im

    @staticmethod
    def _resize_derivative(im, width, height, allow_crop):
        im = im.convert('RGB')
        old_width, old_height = im.size

        def intround(value):
            if isinstance(value, tuple):
                return tuple(intround(v) for v in value)
            elif isinstance(value, float):
                return int(round(value))
            return value

        if width > 0 and height > 0:
            fx = old_width / width
            fy = old_height / height

            if allow_crop:
                f = min(fx, fy)
                crop_size = crop_width, crop_height = width * f, height * f

                trim_x = (old_width - crop_width) / 2
                trim_y = (old_height - crop_height) / 2
                crop = trim_x, trim_y, crop_width + trim_x, crop_height + trim_y

                im = im.transform(intround(crop_size), Image.EXTENT, intround(crop))

                size = width, height
            else:
                f = max(fx, fy)
                size = old_width / f, old_height / f

        elif width > 0 and height is None:
            f = old_width / width
            size = width, old_height / f

        elif height > 0 and width is None:
            f = old_height / height
            size = old_width / f, height

        else:
            return im

        return im.resize(intround(size), Image.ANTIALIAS)

    def _save_derivative(self, im):
        save_kwargs = {
            'image/gif': {'format': 'GIF'},
            'image/jpeg': {'format': 'JPEG', 'quality': 95},
            'image/png': {'format': 'PNG', 'optimize': True}}

        io = StringIO()
        im.save(io, **save_kwargs[self.mime_type])
        self.set_data(io.getvalue())
