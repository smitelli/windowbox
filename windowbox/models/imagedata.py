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

        im = self.data_to_image()
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

        return self.image_to_data(im)

    def data_to_image(self):
        return Image.open(StringIO(self.data))

    def image_to_data(self, image):
        io = StringIO()

        if self.mime_type == 'image/png':
            image.save(io, 'PNG', optimize=True)
        elif self.mime_type == 'image/gif':
            image.save(io, 'GIF')
        else:
            image.save(io, 'JPEG', quality=95)

        return io.getvalue()
