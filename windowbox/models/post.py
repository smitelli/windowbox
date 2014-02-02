import sqlalchemy as sa
import windowbox.configs.base as cfg
from windowbox.database import (
    DeclarativeBase, session as db_session, UTCDateTime)
from windowbox.models import BaseModel


class PostManager():
    def get_all(self):
        for post in db_session.query(Post).order_by(Post.id):
            yield post

    def get_by_id(self, post_id):
        return db_session.query(Post).filter(Post.id == post_id).first()

    def get_adjacent_by_id(self, post_id):
        prev = db_session.query(Post).filter(Post.id < post_id).order_by(sa.desc(Post.id)).first()
        next = db_session.query(Post).filter(Post.id > post_id).order_by(Post.id).first()
        return (prev, next)


class PostSchema(DeclarativeBase):
    __tablename__ = 'posts'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    created_utc = sa.Column(UTCDateTime)
    message = sa.Column(sa.UnicodeText)
    ua = sa.Column(sa.String(255))


class Post(PostSchema, BaseModel):
    def __repr__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)

    @property
    def readable_date(self):
        date_local = self.created_utc.astimezone(cfg.DISPLAY_TIMEZONE)
        return date_local.strftime('%Y-%m-%d %H:%M:%S %Z')
