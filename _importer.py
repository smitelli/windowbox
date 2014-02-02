import csv
import os
import pytz
from datetime import datetime
from windowbox.database import session as db_session
from windowbox.models.post import Post
from windowbox.models.attachment import Attachment, AttachmentDerivative

_path = os.path.abspath(os.path.dirname(__file__))
_tz = pytz.timezone('America/New_York')


def get_attachment_path(id):
    ipath = os.path.join(_path, '_importable/originals/{}.jpg'.format(id))
    if os.path.isfile(ipath):
        return ('image/jpeg', ipath)

    ipath = os.path.join(_path, '_importable/originals/{}.png'.format(id))
    if os.path.isfile(ipath):
        return ('image/png', ipath)

    ipath = os.path.join(_path, '_importable/posts/{}.jpg'.format(id))
    if os.path.isfile(ipath):
        return ('image/jpeg', ipath)

    ipath = os.path.join(_path, '_importable/posts/{}.png'.format(id))
    if os.path.isfile(ipath):
        return ('image/png', ipath)

    return (None, None)

Post.__table__.create()
Attachment.__table__.create()
AttachmentDerivative.__table__.create()

fields = ['post_id', 'attachment_id', 'timestamp', 'message', 'ua']
data = csv.reader(open(os.path.join(_path, '_importable/mob1_posts.csv')))

for row in data:
    # Convert from the miserable CoMoblog post table format
    rowdata = dict(zip(fields, row))

    try:
        body = unicode(rowdata['message'], 'ascii')
    except UnicodeError:
        body = unicode(rowdata['message'], 'utf-8')

    postdata = {
        'id': rowdata['post_id'],
        'created_utc': _tz.localize(datetime.fromtimestamp(float(rowdata['timestamp']))),
        'message': body,
        'ua': rowdata['ua']}

    print 'Inserting post #{}...'.format(rowdata['post_id'])
    post = Post(**postdata).save(commit=True)

    imime, ipath = get_attachment_path(rowdata['attachment_id'])
    attach_data = {
        'post_id': post.id,
        'mime_type': '',
        'exif_data': ''}

    print 'Inserting attachment...'
    attachment = Attachment(**attach_data)
    attachment.set_data_from_file(ipath)
    attachment.save(commit=True)

db_session.close()
