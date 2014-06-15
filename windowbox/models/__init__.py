from __future__ import absolute_import
import errno
import os
from magic import Magic
from windowbox.database import db


class BaseModel(object):
    def save(self, commit=False):
        db.session.add(self)
        db.session.flush()

        if commit:
            db.session.commit()

        return self


class BaseFSEntity(object):
    MIME_EXTENSION_MAP = {}

    def get_storage_path(self):
        raise NotImplementedError()

    def get_file_name(self):
        pk_attribute = db.class_mapper(self.__class__).primary_key[0].name
        id_str = str(getattr(self, pk_attribute))

        try:
            extension = self.MIME_EXTENSION_MAP[self.mime_type]
        except KeyError:
            extension = ''

        if len(id_str) <= 1:
            d1, d2 = ('0', '0')
        elif len(id_str) == 2:
            d1, d2 = ('0', id_str[0])
        else:
            d1, d2 = (id_str[0], id_str[1])

        file_name = '{}{}'.format(id_str, extension)

        return os.path.join(self.get_storage_path(), d1, d2, file_name)

    def get_data(self):
        with open(self.get_file_name(), mode='rb') as fh:
            return fh.read()

    def set_data(self, buffer_str):
        self.mime_type = Magic(mime=True).from_buffer(buffer_str)

        # Ensures we have an auto-increment ID for get_file_name().
        self.save(commit=False)

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
            fh.write(buffer_str)

    def set_data_from_file(self, source_file):
        with open(source_file, mode='rb') as fh:
            self.set_data(fh.read())
