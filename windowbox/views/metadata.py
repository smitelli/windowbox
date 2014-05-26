from flask import render_template

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


class MetadataView(object):
    def __init__(self, metadata):
        self.metadata = metadata

    def render_html(self):
        template_vars = {
            'metadata': self.metadata,
            'camera': self._collect_items(CAMERA_ITEMS),
            'image': self._collect_items(IMAGE_ITEMS),
            'environment': self._collect_items(ENVIRONMENT_ITEMS),
            'hardware': self._collect_items(HARDWARE_ITEMS),
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
