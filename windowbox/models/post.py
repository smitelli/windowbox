import sqlalchemy as sa
import sqlalchemy.orm as orm
from . import Base, sess
from windowbox.models.imagedata import ImageData


class Post(Base):
    __tablename__ = 'posts'
    post_id = sa.Column('id', sa.Integer, primary_key=True)
    image_id = sa.Column(sa.Integer, sa.ForeignKey('image_data.image_id'))
    timestamp = sa.Column(sa.Integer)
    message = sa.Column(sa.String(255))
    ua = sa.Column(sa.String(255))

    image = orm.relationship(ImageData, backref=orm.backref('post', uselist=False))

    def __repr__(self):
        return '<Post id={}>'.format(self.post_id)

    @classmethod
    def get_all(cls):
        return sess.query(cls).order_by(cls.post_id).all()

    @classmethod
    def get_by_id(cls, post_id):
        return sess.query(cls).filter(cls.post_id == post_id).first()

    def get_adjacent(self):
        cls = self.__class__
        prev = sess.query(cls).filter(cls.post_id < self.post_id).order_by(sa.desc(cls.post_id)).first()
        next = sess.query(cls).filter(cls.post_id > self.post_id).order_by(cls.post_id).first()

        return (prev, next)
