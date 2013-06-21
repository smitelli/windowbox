import csv
import os
from windowbox.database import session as db_session
from windowbox.models.post import Post
from windowbox.models.image import ImageOriginal

_path = os.path.abspath(os.path.dirname(__file__))


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

fields = ['post_id', 'image_id', 'timestamp', 'message', 'ua']
data = csv.reader(open(os.path.join(_path, '_importable/mob1_posts.csv')))

for row in data:
    rowdata = dict(zip(fields, row))
    imime, ipath = get_image_path(rowdata['image_id'])

    postdata = {
        'post_id': rowdata['post_id'],
        'timestamp': rowdata['timestamp'],
        'message': rowdata['message'],
        'ua': rowdata['ua']}

    print 'Inserting post #{}...'.format(rowdata['post_id'])
    post = Post(**postdata).create()

    imagedata = {
        'post_id': rowdata['post_id'],
        'mime_type': imime}

    print 'Inserting image...'
    image = ImageOriginal(**imagedata).create()
    image.set_data_from_file(ipath)

db_session.close()
