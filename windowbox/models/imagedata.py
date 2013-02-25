import Image
import sqlalchemy as sa
from StringIO import StringIO
from . import Base


class ImageData(Base):
    __tablename__ = 'image_data'
    image_id = sa.Column(sa.Integer, primary_key=True)
    mime_type = sa.Column(sa.String(64))
    data = sa.Column(sa.LargeBinary)

    def __repr__(self):
        return '<ImageData image_id={}>'.format(self.image_id)

    def get_resized_data(self, width=None, height=None):
        width, height = int(width or 0), int(height or 0)

        im = Image.open(StringIO(self.data))
        old_width, old_height = im.size
        crop = 0, 0, old_width, old_height

        if width and height:
            fx = float(old_width) / width
            fy = float(old_height) / height
            f = fx if fx < fy else fy

            crop_width, crop_height = int(width * f), int(height * f)

            trim_x = (old_width - crop_width) / 2
            trim_y = (old_height - crop_height) / 2

            crop = trim_x, trim_y, crop_width + trim_x, crop_height + trim_y
            size = width, height

        elif width and not height:
            f = float(old_width) / width
            size = width, int(old_height / f)

        elif height and not width:
            f = float(old_height) / height
            size = int(old_width / f), height

        else:
            size = old_width, old_height

        im = im.transform(size, Image.EXTENT, crop, Image.BICUBIC)

        im_io = StringIO()
        im.save(im_io, 'JPEG', quality=100)
        return im_io.getvalue()
