import Image
from StringIO import StringIO

from sqlalchemy import Column, Integer, String, LargeBinary
from database import Base


class Post(Base):
    __tablename__ = 'posts'
    id = Column('id', Integer, primary_key=True)
    image_id = Column('image_id', Integer)
    timestamp = Column('timestamp', Integer)
    message = Column('message', String(255))
    ua = Column('ua', String(255))

    def __init__(self, id=None, image_id=None, timestamp=None, message=None,
                 ua=None):
        self.id = id
        self.image_id = image_id
        self.timestamp = timestamp
        self.message = message
        self.ua = ua

    def __repr__(self):
        return '<Post id={}>'.format(self.id)

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def get_by_id(cls, post_id):
        return cls.query.filter(cls.id == post_id).first()

    def get_image(self):
        return ImageData.get_by_id(self.image_id)


class ImageData(Base):
    __tablename__ = 'image_data'
    image_id = Column('image_id', Integer, primary_key=True)
    mime_type = Column('mime_type', String(64))
    data = Column('data', LargeBinary)

    def __init__(self, image_id=None, mime_type=None, data=None):
        self.image_id = image_id
        self.mime_type = mime_type
        self.data = data

    def __repr__(self):
        return '<ImageData image_id={}>'.format(self.image_id)

    @classmethod
    def get_by_id(cls, image_id):
        return cls.query.filter(cls.image_id == image_id).first()

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

        im = im.transform(size, Image.EXTENT, crop)

        im_io = StringIO()
        im.save(im_io, 'JPEG', quality=100)
        return im_io.getvalue()
