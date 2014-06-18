from __future__ import absolute_import
from collections import defaultdict


class Metadata(object):
    CAMERA_ITEMS = [
        'EXIF.FocalLength',
        'EXIF.FocalLengthIn35mmFormat',
        'Composite.ScaleFactor35efl',
        'EXIF.DigitalZoomRatio',
        ('Composite.ShutterSpeed', 'EXIF.ShutterSpeedValue'),
        'EXIF.ApertureValue',
        'EXIF.ISO',
        'EXIF.Flash',
        'EXIF.WhiteBalance',
        'EXIF.MeteringMode',
        'EXIF.ExposureMode',
        'EXIF.ExposureProgram',
        'EXIF.ExposureTime',
        'EXIF.FNumber',
        'Composite.CircleOfConfusion',
        'Composite.FOV',
        'Composite.HyperfocalDistance',
        'EXIF.BrightnessValue',
        'Composite.LightValue']

    IMAGE_ITEMS = [
        ('PNG.ImageWidth', 'EXIF.ExifImageWidth', 'File.ImageWidth'),
        ('PNG.ImageHeight', 'EXIF.ExifImageHeight', 'File.ImageHeight'),
        'EXIF.Orientation',
        ('EXIF.XResolution', 'JFIF.XResolution'),
        ('EXIF.YResolution', 'JFIF.YResolution'),
        ('EXIF.ResolutionUnit', 'JFIF.ResolutionUnit'),
        'MakerNotes.HDRImageType',
        'EXIF.Gamma',
        'EXIF.Sharpness',
        'EXIF.SensingMethod',
        'EXIF.SceneType',
        'EXIF.SceneCaptureType',
        'EXIF.SubjectArea',
        'EXIF.SubjectDistanceRange',
        'PNG.Filter',
        'PNG.Interlace',
        ('PNG.BitDepth', 'File.BitsPerSample'),
        ('PNG.ColorType', 'EXIF.ColorSpace'),
        'File.ColorComponents',
        'EXIF.ComponentsConfiguration',
        'EXIF.YCbCrPositioning',
        'File.YCbCrSubSampling',
        'File.FileType',
        'File.FileSize',
        ('PNG.Compression', 'EXIF.Compression'),
        'File.EncodingProcess',
        'File.ExifByteOrder']

    ENVIRONMENT_ITEMS = [
        'EXIF.Software',
        'EXIF.ExifVersion',
        'EXIF.FlashpixVersion',
        'JFIF.JFIFVersion',
        'XMP.XMPToolkit',
        'EXIF.InteropVersion',
        'EXIF.InteropIndex',
        'Composite.RunTimeSincePowerUp']

    HARDWARE_ITEMS = [
        'EXIF.Make',
        'EXIF.Model',
        'EXIF.LensMake',
        'EXIF.LensModel',
        'EXIF.LensInfo']

    GPS_ITEMS = [
        'Composite.GPSAltitude',
        'Composite.GPSLatitude',
        'Composite.GPSLongitude',
        'Composite.GPSPosition',
        'EXIF.GPSDOP',
        'EXIF.GPSImgDirection',
        'EXIF.GPSImgDirectionRef']

    def __init__(self, attributes):
        self.items = defaultdict(MetadataItem)

        for key, data in attributes.iteritems():
            item_key, kind = key.rsplit('.', 1)
            self.items[item_key].add_data(kind, data)

        for key, item in self.items.iteritems():
            item.key = key

    def __getitem__(self, item_key):
        if self.items[item_key].is_built():
            return self.items[item_key]
        else:
            return None

    def get_categories(self):
        return {
            'camera': self._collect_items(self.CAMERA_ITEMS),
            'image': self._collect_items(self.IMAGE_ITEMS),
            'environment': self._collect_items(self.ENVIRONMENT_ITEMS),
            'hardware': self._collect_items(self.HARDWARE_ITEMS),
            'gps': self._collect_items(self.GPS_ITEMS)}

    def to_dict(self):
        result = {}
        for category, items in self.get_categories().iteritems():
            result[category] = [i.to_dict() for i in items]

        return result

    def _collect_items(self, category):
        items = [self._lookup_item(key) for key in category]

        return [itm for itm in items if itm is not None]

    def _lookup_item(self, key):
        if not isinstance(key, tuple):
            key = (key, )

        for candidate in key:
            item = self[candidate]
            if item:
                return item

        return None


class MetadataItem(object):
    def __init__(self):
        self.key = None
        self.description = None
        self.raw_value = None
        self.value = None

    def __repr__(self):
        return '<{} key={}>'.format(self.__class__.__name__, self.key)

    def add_data(self, kind, data):
        if kind == 'desc':
            self.description = data
        elif kind == 'num':
            self.raw_value = data
        elif kind == 'val':
            self.value = data
        else:
            raise AttributeError('Unknown kind {}'.format(kind))

    def is_built(self):
        if not (self.description or self.key):
            return False
        elif not (self.value or self.raw_value):
            return False
        else:
            return True

    def to_dict(self):
        return {
            'key': self.key,
            'description': self.description,
            'raw_value': self.raw_value,
            'value': self.value}

    @property
    def display_name(self):
        return self.description or '<{}>'.format(self.key)

    @property
    def display_value(self):
        return self.value or '<{}>'.format(self.raw_value)
