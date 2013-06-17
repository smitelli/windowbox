import sqlalchemy as sa
import sqlalchemy.orm as orm
from windowbox.database import Base


class ImageDataSchema(Base):
    __tablename__ = 'image_data'
    image_id = sa.Column(sa.Integer, primary_key=True)
    mime_type = sa.Column(sa.String(64))
    data = sa.Column(sa.LargeBinary)


class PostSchema(Base):
    __tablename__ = 'posts'
    post_id = sa.Column('id', sa.Integer, primary_key=True)
    image_id = sa.Column(sa.Integer, sa.ForeignKey('image_data.image_id'))
    timestamp = sa.Column(sa.Integer)
    message = sa.Column(sa.String(255))
    ua = sa.Column(sa.String(255))

    from windowbox.models.imagedata import ImageData
    image = orm.relationship(ImageData, backref=orm.backref('post', uselist=False))
