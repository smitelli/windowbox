from __future__ import absolute_import
from flask import current_app
from windowbox.application import app
from windowbox.models.attachment import Attachment

with app.app_context():
    bads = Attachment.query.filter(
        Attachment.geo_latitude.isnot(None), Attachment.geo_longitude.isnot(None),
        Attachment.geo_address.is_(None)).all()

    for bad in bads:
        print 'Fixing geo address on attachment #{}'.format(bad.id)
        bad.geo_address = Attachment._load_address_data(
            bad.geo_latitude, bad.geo_longitude, current_app.config['GOOGLE_API_KEY'])
        bad.save(commit=True)
