from datetime import time
from PIL import ExifTags
from windowbox.models import ImageOriginalSchema


class xxxImageData(ImageOriginalSchema):
    def get_exif_data(self, im):
        try:
            exif = im._getexif()
        except (AttributeError, IOError):
            return None

        if exif:
            return xxxExifData(exif).todict()

        return None


class xxxExifData():
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
                    value = time(hour % 24, mins % 60, secs % 60, msec).isoformat()
                else:
                    # Scalar value, pass through
                    value = v

                data[key] = value

        return data
