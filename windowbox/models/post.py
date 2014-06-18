from __future__ import absolute_import
from calendar import timegm
from email.utils import formatdate
from flask import current_app
from windowbox.database import UTCDateTime, db
from windowbox.models import BaseModel
from windowbox.models.attachment import AttachmentManager


class PostManager(object):
    @staticmethod
    def get_all(until_id=None, limit=None):
        qu = Post.query.order_by(Post.id.desc())

        if until_id is not None:
            qu = qu.filter(Post.id < until_id)

        if limit is not None:
            qu = qu.limit(limit + 1)

        posts = qu.all()

        if limit is not None:
            has_next = (len(posts) > limit)
            return (posts[:limit], has_next)

        return (posts, False)

    @staticmethod
    def get_by_id(post_id):
        return Post.query.filter_by(id=post_id).first()

    @staticmethod
    def get_adjacent_by_id(post_id):
        prev = Post.query.filter(Post.id < post_id).order_by(Post.id.desc()).first()
        next = Post.query.filter(Post.id > post_id).order_by(Post.id.asc()).first()

        return (prev, next)


class Post(db.Model, BaseModel):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_utc = db.Column(UTCDateTime)
    message = db.Column(db.UnicodeText)
    user_agent = db.Column(db.String(255))

    def __repr__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)

    def get_attachment(self):
        return AttachmentManager.get_by_post_id(self.id)

    def get_created_date(self, format=None):
        if format is None:
            format = '%Y-%m-%d %H:%M:%S %Z'

        created_local = self.created_utc.astimezone(current_app.config['DISPLAY_TIMEZONE'])

        return created_local.strftime(format)

    def get_created_date_rfc822(self):
        return formatdate(timegm(self.created_utc.timetuple()))

    def to_dict(self, lookup_children=False):
        data = {
            'id': self.id,
            'created': self.created_utc.isoformat(),
            'message': self.message,
            'user_agent': self.user_agent}

        if lookup_children:
            data['attachment'] = self.get_attachment().to_dict(lookup_children=True)

        return data
