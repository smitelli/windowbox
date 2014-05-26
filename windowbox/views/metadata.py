from flask import render_template

OPTICAL_ITEMS = [
    'Composite.CircleOfConfusion',
    'Composite.FOV',
    'Composite.HyperfocalDistance',
    'Composite.LightValue',
    'Composite.ScaleFactor35efl',
    ('Composite.ShutterSpeed', 'EXIF.ShutterSpeedValue'),
    'EXIF.ApertureValue',
    'EXIF.BrightnessValue',
    'EXIF.DigitalZoomRatio',
    'EXIF.ExposureMode',
    'EXIF.ExposureProgram',
    'EXIF.ExposureTime',
    'EXIF.FNumber',
    'EXIF.Flash',
    'EXIF.FocalLength',
    'EXIF.FocalLengthIn35mmFormat',
    'EXIF.ISO',
    'EXIF.MeteringMode',
    'EXIF.WhiteBalance']

IMAGE_ITEMS = [
    ('PNG.ColorType', 'EXIF.ColorSpace'),
    'EXIF.ComponentsConfiguration',
    ('PNG.Compression', 'EXIF.Compression'),
    ('PNG.ImageHeight', 'EXIF.ExifImageHeight', 'File.ImageHeight'),
    ('PNG.ImageWidth', 'EXIF.ExifImageWidth', 'File.ImageWidth'),
    'EXIF.Gamma',
    'EXIF.Orientation',
    ('EXIF.ResolutionUnit', 'JFIF.ResolutionUnit'),
    'EXIF.SceneCaptureType',
    'EXIF.SceneType',
    'EXIF.SensingMethod',
    'EXIF.Sharpness',
    'EXIF.SubjectArea',
    'EXIF.SubjectDistanceRange',
    ('EXIF.XResolution', 'JFIF.XResolution'),
    ('EXIF.YResolution', 'JFIF.YResolution'),
    'EXIF.YCbCrPositioning',
    ('PNG.BitDepth', 'File.BitsPerSample'),
    'File.ColorComponents',
    'File.EncodingProcess',
    'File.ExifByteOrder',
    'File.FileSize',
    'File.FileType',
    'File.YCbCrSubSampling',
    'MakerNotes.HDRImageType',
    'PNG.Filter',
    'PNG.Interlace']

SOFTWARE_ITEMS = [
    'Composite.RunTimeSincePowerUp',
    'EXIF.ExifVersion',
    'EXIF.FlashpixVersion',
    'EXIF.InteropIndex',
    'EXIF.InteropVersion',
    'EXIF.Software',
    'JFIF.JFIFVersion',
    'XMP.XMPToolkit']

PHYSICAL_ITEMS = [
    'EXIF.LensInfo',
    'EXIF.LensMake',
    'EXIF.LensModel',
    'EXIF.Make',
    'EXIF.Model']

GPS_ITEMS = [
    'Composite.GPSAltitude',
    'Composite.GPSLatitude',
    'Composite.GPSLongitude',
    'Composite.GPSPosition',
    'EXIF.GPSDOP',
    'EXIF.GPSImgDirection',
    'EXIF.GPSImgDirectionRef']


class MetadataView(object):
    def __init__(self, metadata):
        self.metadata = metadata

    def render_html(self):
        template_vars = {
            'metadata': self.metadata,
            'optical': self._collect_items(OPTICAL_ITEMS),
            'image': self._collect_items(IMAGE_ITEMS),
            'software': self._collect_items(SOFTWARE_ITEMS),
            'physical': self._collect_items(PHYSICAL_ITEMS),
            'gps': self._collect_items(GPS_ITEMS)}

        return render_template('metadata.html', **template_vars)

    def _collect_items(self, category):
        items = [self._lookup_item(key) for key in category]

        return [itm for itm in items if itm is not None]

    def _lookup_item(self, key):
        if not isinstance(key, tuple):
            key = (key, )

        for candidate in key:
            item = self.metadata[candidate]
            if item.is_built():
                return item

        return None
