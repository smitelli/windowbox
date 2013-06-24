import csv
import os
import pytz
from datetime import datetime
from windowbox.database import session as db_session
from windowbox.models.post import Post
from windowbox.models.image import ImageOriginal, ImageDerivative

_path = os.path.abspath(os.path.dirname(__file__))
_tz = pytz.timezone('America/New_York')


def get_image_path(id):
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
ImageOriginal.__table__.create()
ImageDerivative.__table__.create()

fields = ['post_id', 'image_id', 'timestamp', 'message', 'ua']
data = csv.reader(open(os.path.join(_path, '_importable/mob1_posts.csv')))

for row in data:
    # Convert from the miserable CoMoblog post table format
    rowdata = dict(zip(fields, row))

    try:
        body = unicode(rowdata['message'], 'ascii')
    except UnicodeError:
        body = unicode(rowdata['message'], 'utf-8')

    postdata = {
        'post_id': rowdata['post_id'],
        'date_gmt': _tz.localize(datetime.fromtimestamp(float(rowdata['timestamp']))),
        'message': body,
        'ua': rowdata['ua']}

    print 'Inserting post #{}...'.format(rowdata['post_id'])
    post = Post(**postdata).save(commit=True)

    imime, ipath = get_image_path(rowdata['image_id'])
    imagedata = {
        'post_id': post.post_id,
        'mime_type': '',
        'exif_data': ''}

    print 'Inserting image...'
    image = ImageOriginal(**imagedata)
    image.set_data_from_file(ipath)
    image.save(commit=True)

db_session.close()
