"""
Model serialzation classes.

These are just about on the edge of needing to be refactored using some kind of
library designed for this sort of thing. Any time there is a sub-schema or a
dict/list comprehension is an opportunity to offload work to something else.

If the day ever comes when POST/PUT/PATCH methods need to be supported and
validation comes into play, it will be time to put this approach away.
"""

from flask import url_for
from windowbox.models.attachment import EXIF_CATEGORIES


def attachment_url(a):
    return url_for('.get_attachment', attachment_id=a.id, _external=True)


def post_url(p):
    return url_for('.get_post', post_id=p.id, _external=True)


class AttachmentSchema:
    """
    Class for serializing an Attachment (abbreviated view) to JSON.
    """
    THUMBNAIL_KINDS = ('thumbnail', 'thumbnail2x')

    def __init__(self, attachment):
        self.attachment = attachment

    def deriv_url(self, dim_name):
        return self.attachment.derivative_url(dim_name, _external=True)

    def to_dict(self):
        return {
            'id': self.attachment.id,
            'mime_type': self.attachment.mime_type,
            'self_url': attachment_url(self.attachment),
            **{f'{n}_url': self.deriv_url(n) for n in self.THUMBNAIL_KINDS}}


class AttachmentSchemaFull(AttachmentSchema):
    """
    Class for serializing an Attachment (complete view) to JSON.

    Note: If Derivatives are ever extended to support different mime_types than
    their Attachments (think image thumbnail for a video file), the generation
    of mime_type will need to be rethought.

    Note: geo_latitude and geo_longitude are intentionally redacted here for
    privacy reasons.
    """
    def to_dict(self):
        all_dimensions = self.attachment.CANNED_DIMENSIONS_MAP.items()

        return {
            **super().to_dict(),
            # 'geo_latitude': float(self.attachment.geo_latitude),
            # 'geo_longitude': float(self.attachment.geo_longitude),
            'geo_address': self.attachment.geo_address,
            'derivatives': {
                canned_dimensions: {
                    **dim_tuple._asdict(),
                    'mime_type': self.attachment.mime_type,
                    'url': self.deriv_url(canned_dimensions)}
                for canned_dimensions, dim_tuple in all_dimensions},
            'exif': {
                k: [f._asdict() for f in self.attachment.yield_exif(k)] for k in
                EXIF_CATEGORIES.keys()}}


class PostSchema:
    """
    Class for serializing a Post (abbreviated view) to JSON.
    """

    def __init__(self, post):
        self.post = post

    def to_dict(self):
        return {
            'id': self.post.id,
            'created_utc': self.post.created_utc.isoformat(),
            'caption': self.post.caption,
            'self_url': post_url(self.post),
            'attachments': [
                AttachmentSchema(a).to_dict() for a in self.post.attachments]}


class PostSchemaFull(PostSchema):
    """
    Class for serializing a Post (complete view) to JSON.
    """

    def to_dict(self):
        return {
            **super().to_dict(),
            'user_agent': self.post.user_agent,
            'is_barked': self.post.is_barked,
            'sender': SenderSchema(self.post.sender).to_dict()}


class SenderSchema:
    """
    Class for serializing a Sender to JSON.

    Note: email_address is intentionally redacted here to avoid spam and issues
    with privacy.
    """

    def __init__(self, sender):
        self.sender = sender

    def to_dict(self):
        return {
            'id': self.sender.id,
            # 'email_address': self.sender.email_address,
            'created_utc': self.sender.created_utc.isoformat(),
            'display_name': self.sender.display_name}
