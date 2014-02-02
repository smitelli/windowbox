import errno
import os
import sqlalchemy as sa
from magic import Magic
from windowbox.database import session


class BaseModel():
    def save(self, commit=False):
        session.add(self)
        session.flush()

        if commit:
            session.commit()

        return self


class BaseFSEntity():
    storage_path = ''
    mime_extension_map = {}

    def get_data(self):
        with open(self.get_file_name(), mode='rb') as fh:
            data = fh.read()

        return data

    def set_data(self, data):
        # Need to save() to ensure we know our auto-increment ID
        self.save(commit=False)

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

    def get_file_name(self):
        primary_key = sa.orm.class_mapper(self.__class__).primary_key[0].name
        id_str = str(getattr(self, primary_key))

        extension = ''
        try:
            extension = self.mime_extension_map[self.mime_type]
        except KeyError:
            pass

        if len(id_str) <= 1:
            d1, d2 = ('0', '0')
        elif len(id_str) == 2:
            d1, d2 = ('0', id_str[0])
        else:
            d1, d2 = (id_str[0], id_str[1])

        file_name = '{}{}'.format(id_str, extension)

        return os.path.join(self.storage_path, d1, d2, file_name)

    def _identify_mime_type(self, buffer):
        magic = Magic(mime=True)
        return magic.from_buffer(buffer)
