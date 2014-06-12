from __future__ import absolute_import
from windowbox.application import app
from windowbox.models.attachment import Attachment

with app.app_context():
    bads = Attachment.query.filter(Attachment.geo_latitude.isnot(None)) \
        .filter(Attachment.geo_address.is_(None)).all()

    for bad in bads:
        print 'Fixing geo address on attachment {}'.format(bad.id)
        bad.geo_address = Attachment._load_address_data(bad.geo_latitude, bad.geo_longitude)
        bad.save(commit=True)
