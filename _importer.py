import csv
import os

from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, LargeBinary


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

fn = os.path.join(_path, 'db.sqlite')
fn = "/home/ssmitelli/db.sqlite"
engine = create_engine('sqlite:///{}'.format(fn), echo=False)
metadata = MetaData()

# Post table schema
posts = Table('posts', metadata,
    Column('id', Integer, primary_key=True),
    Column('image_id', Integer),
    Column('timestamp', Integer),
    Column('message', String(255)),
    Column('ua', String(255)))

# Image data schema
image_data = Table('image_data', metadata,
    Column('image_id', Integer, primary_key=True),
    Column('mime_type', String(64)),
    Column('data', LargeBinary))

# Ensure tables exist, create if not
metadata.create_all(engine)

session = engine.connect()

data = csv.reader(open(os.path.join(_path, '_importable/mob1_posts.csv')))
fields = ['id', 'image_id', 'timestamp', 'message', 'ua']

for row in data:
    # Insert post data from the CSV file
    items = zip(fields, row)
    item = {}

    for (name, value) in items:
        item[name] = value.strip()

    print 'Inserting post #{}...'.format(item['id'])
    session.execute(posts.insert().values(**item))

    # Insert image data from the filesystem
    itype, ipath = get_image_path(item['image_id'])

    if itype and ipath:
        f = open(ipath, 'r')
        data = {
            'image_id': item['image_id'],
            'mime_type': itype,
            'data': f.read()}

        print '    (image #{})'.format(item['image_id'])
        session.execute(image_data.insert().values(**data))

session.close()
