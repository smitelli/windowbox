import sqlalchemy as sa
from windowbox.database import DeclarativeBase, session


class PostSchema(DeclarativeBase):
    __tablename__ = 'posts'
    post_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    timestamp = sa.Column(sa.Integer)
    message = sa.Column(sa.String(255))
    ua = sa.Column(sa.String(255))


class ImageOriginalSchema(DeclarativeBase):
    __tablename__ = 'image_originals'
    post_id = sa.Column(sa.Integer, primary_key=True)
    mime_type = sa.Column(sa.String(64))


class BaseModel():
    def create(self):
        session.add(self)

        session.commit()

        return self

    def save(self, force=False):
        session.add(self)

        if force:
            session.flush()

        return self
