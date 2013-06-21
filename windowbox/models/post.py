from datetime import datetime
import sqlalchemy as sa
from windowbox.database import session as db_session
from windowbox.models import PostSchema, BaseModel


class PostFactory():
    def get_all(self):
        for post in db_session.query(Post).order_by(Post.post_id):
            yield post

    def get_by_id(self, post_id):
        return db_session.query(Post).filter(Post.post_id == post_id).first()

    def get_adjacent_by_id(self, post_id):
        prev = db_session.query(Post).filter(Post.post_id < post_id).order_by(sa.desc(Post.post_id)).first()
        next = db_session.query(Post).filter(Post.post_id > post_id).order_by(Post.post_id).first()
        return (prev, next)


class Post(PostSchema, BaseModel):
    def __repr__(self):
        return '<Post id={}>'.format(self.post_id)

    @property
    def readable_date(self):
        ts = datetime.fromtimestamp(self.timestamp)
        return ts.strftime('%Y-%m-%d %H:%M:%S')
