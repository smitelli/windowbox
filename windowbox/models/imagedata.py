from datetime import time
from StringIO import StringIO
from PIL import Image, ExifTags
from windowbox.models import ImageDataSchema


class ImageData(ImageDataSchema):
    def __repr__(self):
        return '<ImageData image_id={}>'.format(self.image_id)

    def get_resized_data(self, width=None, height=None):
        width, height = int(width or 0), int(height or 0)

        im = self._data_to_image()
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
            size = old_width, old_height

        im = im.resize(size, Image.ANTIALIAS)

        return self._image_to_data(im)

    def get_exif_data(self):
        exif = self._data_to_image()._getexif()

        if exif:
            ex = ExifData(exif).todict()
            #TODO
            from pprint import pprint; pprint(ex)
        else:
            print "No exif!"

    def _data_to_image(self):
        return Image.open(StringIO(self.data))

    def _image_to_data(self, image):
        io = StringIO()

        if self.mime_type == 'image/png':
            image.save(io, 'PNG', optimize=True)
        elif self.mime_type == 'image/gif':
            image.save(io, 'GIF')
        else:
            image.save(io, 'JPEG', quality=95)

        return io.getvalue()


class ExifData():
    DEEP_KEYS = {
        'GPSInfo': ExifTags.GPSTAGS}
    _parsed_dict = None

    def __init__(self, raw_exif=None):
        self._parsed_dict = self._dict_from_exif(raw_exif)

    def todict(self):
        return self._parsed_dict

    def _dict_from_exif(self, source, tags=ExifTags.TAGS):
        data = {}
        for k, v in source.items():
            key = tags.get(k, k)

            if key in self.DEEP_KEYS:
                deep_data = self._dict_from_exif(v, self.DEEP_KEYS[key])
                data.update(deep_data)
            else:
                if isinstance(v, tuple) and len(v) == 2:
                    # Decode rational value
                    value = float(v[0]) / v[1]
                elif key in ['GPSLatitude', 'GPSLongitude']:
                    # Decode GPS lat/lon value
                    degs = float(v[0][0]) / v[0][1]
                    mins = float(v[1][0]) / v[1][1]
                    secs = float(v[2][0]) / v[2][1]
                    value = degs + (mins / 60) + (secs / 3600)
                elif key == 'GPSTimeStamp':
                    # Decode GPS timestamp
                    hour = v[0][0] / v[0][1]
                    mins = v[1][0] / v[1][1]
                    secs, msec = divmod(v[2][0], v[2][1])
                    msec = int((float(msec) / v[2][1]) * 1000000)
                    value = time(hour, mins, secs, msec).isoformat()
                else:
                    # Scalar value, pass through
                    value = v
                
                data[key] = value

        return data;
