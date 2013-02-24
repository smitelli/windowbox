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
        return '<Post {}>'.format(self.id)

    def get_image(self):
        return ImageData.query.filter(ImageData.image_id == self.id).first()


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
        return '<ImageData {}>'.format(self.image_id)
