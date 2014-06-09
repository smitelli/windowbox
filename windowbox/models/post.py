import windowbox.configs.base as cfg
from calendar import timegm
from email.utils import formatdate
from windowbox.database import db, UTCDateTime
from windowbox.models import BaseModel
from windowbox.models.attachment import AttachmentManager


class PostManager():
    @staticmethod
    def get_all(until_id=None, limit=None):
        query = db.session.query(Post).order_by(Post.id.desc())

        if until_id is not None:
            query = query.filter(Post.id < until_id)

        if limit is not None:
            query = query.limit(limit + 1)

        posts = query.all()

        if limit is not None:
            has_next = (len(posts) > limit)
            return (posts[:limit], has_next)

        return (posts, False)

    @staticmethod
    def get_by_id(post_id):
        return db.session.query(Post).filter(Post.id == post_id).first()

    @staticmethod
    def get_adjacent_by_id(post_id):
        prev = db.session.query(Post).filter(Post.id < post_id).order_by(db.desc(Post.id)).first()
        next = db.session.query(Post).filter(Post.id > post_id).order_by(Post.id).first()

        return (prev, next)


class PostSchema(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_utc = db.Column(UTCDateTime)
    message = db.Column(db.UnicodeText)
    user_agent = db.Column(db.String(255))


class Post(PostSchema, BaseModel):
    def __repr__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)

    def get_attachment(self):
        return AttachmentManager.get_by_post_id(self.id)

    def get_created_date(self, format=None):
        if format is None:
            format = '%Y-%m-%d %H:%M:%S %Z'

        created_local = self.created_utc.astimezone(cfg.DISPLAY_TIMEZONE)

        return created_local.strftime(format)

    def get_created_date_rfc822(self):
        return formatdate(timegm(self.created_utc.timetuple()))
