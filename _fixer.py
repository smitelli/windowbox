from windowbox.database import session as db_session
from windowbox.models.attachment import Attachment
from windowbox.models.post import Post

assert Post

bads = db_session.query(Attachment).filter(Attachment.geo_latitude.isnot(None)) \
    .filter(Attachment.geo_address.is_(None)).all()

for bad in bads:
    print bad.id
    bad.geo_address = Attachment._load_address_data(bad.geo_latitude, bad.geo_longitude)
    bad.save(commit=True)

db_session.close()
