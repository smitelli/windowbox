import csv
import os
import pytz
from datetime import datetime
from windowbox.database import session as db_session
from windowbox.models.post import Post
from windowbox.models.attachment import Attachment, AttachmentDerivative, AttachmentAttributesSchema

_path = os.path.abspath(os.path.dirname(__file__))
_tz = pytz.timezone('America/New_York')
_fields = ['post_id', 'attachment_id', 'timestamp', 'message', 'user_agent']


def get_attachment_path(attachment_id):
    checks = [
        '_importable/originals/{}.jpg',
        '_importable/originals/{}.png',
        '_importable/posts/{}.jpg',
        '_importable/posts/{}.png']

    for check in checks:
        attachment_path = os.path.join(_path, check.format(attachment_id))
        if os.path.isfile(attachment_path):
            return attachment_path
    raise Exception

Post.__table__.create()
Attachment.__table__.create()
AttachmentDerivative.__table__.create()
AttachmentAttributesSchema.__table__.create()

with open(os.path.join(_path, '_importable/mob1_posts.csv')) as fh:
    for row in csv.reader(fh):
        row_data = dict(zip(_fields, row))

        created = _tz.localize(datetime.fromtimestamp(float(row_data['timestamp'])))

        try:
            body = row_data['message'].decode('ascii', errors='strict')
        except UnicodeError:
            body = row_data['message'].decode('utf_8', errors='strict')

        post_data = {
            'id': row_data['post_id'],
            'created_utc': created,
            'message': body,
            'user_agent': row_data['user_agent']}

        print 'Inserting post #{}...'.format(row_data['post_id'])
        post = Post(**post_data).save(commit=True)

        attach_data = {
            'post_id': post.id}

        print 'Inserting attachment...'
        attachment = Attachment(**attach_data)
        attachment.set_data_from_file(get_attachment_path(row_data['attachment_id']))
        attachment.save(commit=True)

db_session.close()
