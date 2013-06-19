import csv
import os
from windowbox.database import session as db_session
from windowbox.models.post import Post
from windowbox.models.imagedata import ImageData


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

data = csv.reader(open(os.path.join(_path, '_importable/mob1_posts.csv')))
fields = ['post_id', 'image_id', 'timestamp', 'message', 'ua']

Post.__table__.create()
ImageData.__table__.create()

for row in data:
    item = dict(zip(fields, row))

    print 'Inserting post #{}...'.format(item['post_id'])
    Post(**item).save()

    itype, ipath = get_image_path(item['image_id'])
    f = open(ipath, 'r')
    data = {
        'image_id': item['image_id'],
        'mime_type': itype,
        'data': f.read()}

    print '\tand image #{}...'.format(item['image_id'])
    ImageData(**data).save()

    db_session.flush()

db_session.commit()
db_session.close()