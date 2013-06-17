from datetime import datetime
import sqlalchemy as sa
from windowbox.database import sess
from windowbox.models import PostSchema


class Post(PostSchema):
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

    @property
    def readable_date(self):
        ts = datetime.fromtimestamp(self.timestamp)
        return ts.strftime('%Y-%m-%d %H:%M:%S')
