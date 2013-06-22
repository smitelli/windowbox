import errno
import os
import sqlalchemy as sa
from magic import Magic
import windowbox.configs.base as cfg
from windowbox.database import DeclarativeBase, JSONEncodedDict, session


class PostSchema(DeclarativeBase):
    __tablename__ = 'posts'
    post_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    timestamp = sa.Column(sa.Integer)
    message = sa.Column(sa.Text)
    ua = sa.Column(sa.String(255))


class ImageOriginalSchema(DeclarativeBase):
    __tablename__ = 'image_originals'
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.post_id'), primary_key=True, autoincrement=False)
    mime_type = sa.Column(sa.String(255))
    exif_data = sa.Column(JSONEncodedDict)


class ImageDerivativeSchema(DeclarativeBase):
    __tablename__ = 'image_derivatives'
    __table_args__ = (sa.Index('post_id_and_size', 'post_id', 'size'), )
    derivative_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.post_id'))
    size = sa.Column(sa.String(11))
    mime_type = sa.Column(sa.String(255))


class BaseModel():
    def save(self, commit=False):
        session.add(self)

        if commit:
            session.commit()

        return self


class BaseFSEntity():
    STORAGE_DIR = cfg.STORAGE_DIR
    MIME_EXTENSION_MAP = {}

    def set_data(self, data):
        self.mime_type = self._identify_mime_type(data)

        file_name = self.get_file_name()
        path = os.path.dirname(file_name)

        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

        with open(file_name, mode='wb') as fh:
            fh.write(data)

    def set_data_from_file(self, source_file):
        with open(source_file, mode='rb') as fh:
            data = fh.read()

        self.set_data(data)

    def get_data(self):
        with open(self.get_file_name(), mode='rb') as fh:
            data = fh.read()

        return data

    def get_file_name(self):
        primary_key = sa.orm.class_mapper(self.__class__).primary_key[0].name
        id_str = str(getattr(self, primary_key))

        extension = ''
        try:
            extension = self.MIME_EXTENSION_MAP[self.mime_type]
        except KeyError:
            pass

        if len(id_str) <= 1:
            d1, d2 = ('0', '0')
        elif len(id_str) == 2:
            d1, d2 = ('0', id_str[0])
        else:
            d1, d2 = (id_str[0], id_str[1])

        file_name = '{}{}'.format(id_str, extension)

        return os.path.join(self.STORAGE_DIR, d1, d2, file_name)

    def _identify_mime_type(self, buffer):
        magic = Magic(mime=True)
        return magic.from_buffer(buffer)
