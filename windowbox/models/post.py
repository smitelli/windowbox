import sqlalchemy as sa
import windowbox.configs.base as cfg
from windowbox.database import (
    DeclarativeBase, session as db_session, UTCDateTime)
from windowbox.models import BaseModel
from windowbox.models.attachment import AttachmentManager


class PostManager():
    @staticmethod
    def get_all(until_id=None, limit=None):
        if until_id is not None:
            query = db_session.query(Post).filter(Post.id < until_id).order_by(Post.id.desc()).limit(limit)
        else:
            query = db_session.query(Post).order_by(Post.id.desc()).limit(limit)

        for post in query:
            yield post

    @staticmethod
    def get_by_id(post_id):
        return db_session.query(Post).filter(Post.id == post_id).first()

    @staticmethod
    def get_adjacent_by_id(post_id):
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

    def get_attachment(self):
        return AttachmentManager.get_by_post_id(self.id)

    def get_created_date(self, format=None):
        if format is None:
            format = '%Y-%m-%d %H:%M:%S %Z'

        date_local = self.created_utc.astimezone(cfg.DISPLAY_TIMEZONE)

        return date_local.strftime(format)
