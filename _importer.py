import csv
import os

from sqlalchemy import Table, Column, Integer, String, LargeBinary
from sqlsoup import SQLSoup


def get_image_path(id):
    ipath = '_importable/originals/{}.jpg'.format(id)
    if os.path.isfile(ipath):
        return ('image/jpeg', ipath)

    ipath = '_importable/originals/{}.png'.format(id)
    if os.path.isfile(ipath):
        return ('image/png', ipath)

    ipath = '_importable/posts/{}.jpg'.format(id)
    if os.path.isfile(ipath):
        return ('image/jpeg', ipath)

    ipath = '_importable/posts/{}.png'.format(id)
    if os.path.isfile(ipath):
        return ('image/png', ipath)

    return (None, None)

db = SQLSoup('sqlite:///windowbox.sqlite')

# Post table schema
posts = Table('posts', db._metadata,
    Column('id', Integer, primary_key=True),
    Column('image_id', Integer),
    Column('timestamp', Integer),
    Column('message', String(255)),
    Column('ua', String(255)))

# Image data schema
image_data = Table('image_data', db._metadata,
    Column('image_id', Integer, primary_key=True),
    Column('mime_type', String(64)),
    Column('data', LargeBinary))

# Ensure tables exist, create if not
if not db.engine.has_table('posts'):
    posts.create()

if not db.engine.has_table('image_data'):
    image_data.create()

data = csv.reader(open('_importable/mob1_posts.csv'))
fields = ['id', 'image_id', 'timestamp', 'message', 'ua']

for row in data:
    # Insert post data from the CSV file
    items = zip(fields, row)
    item = {}

    for (name, value) in items:
        item[name] = value.strip()

    print 'Inserting post #{}...'.format(item['id'])
    db.posts.insert(**item)

    # Insert image data from the filesystem
    itype, ipath = get_image_path(item['image_id'])

    if itype and ipath:
        f = open(ipath, 'r')
        data = {
            'image_id': item['image_id'],
            'mime_type': itype,
            'data': f.read()}

        print '    (image #{})'.format(item['image_id'])
        db.image_data.insert(**data)

db.commit()
