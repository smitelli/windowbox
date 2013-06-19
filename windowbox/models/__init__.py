import sqlalchemy as sa
from windowbox.database import DeclarativeBase, session


class PostSchema(DeclarativeBase):
    __tablename__ = 'posts'
    post_id = sa.Column(sa.Integer, primary_key=True)
    image_id = sa.Column(sa.Integer, sa.ForeignKey('image_data.image_id'))
    timestamp = sa.Column(sa.Integer)
    message = sa.Column(sa.String(255))
    ua = sa.Column(sa.String(255))


class ImageDataSchema(DeclarativeBase):
    __tablename__ = 'image_data'
    image_id = sa.Column(sa.Integer, primary_key=True)
    mime_type = sa.Column(sa.String(64))
    data = sa.Column(sa.LargeBinary)

class BaseModel():
    def save(self, force=False):
        session.add(self)
        if force:
            session.flush()
