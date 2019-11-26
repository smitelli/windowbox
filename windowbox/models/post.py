"""
Post model.

Attributes:
    NEWLINE_RUN_MATCHER: Compiled regex to locate runs of two or more
        consecutive newline characters in caption text.
    SIGNATURE_MATCHER: Compiled regex to locate the split-point of an email
        signature in caption text.
"""

import re
from windowbox.database import db
from windowbox.models.sender import Sender

NEWLINE_RUN_MATCHER = re.compile(r'\n{2,}')
SIGNATURE_MATCHER = re.compile(r'^\s*-+\s*$', flags=re.MULTILINE)


class Post(db.Model):
    """
    Post model.

    A Post is analogous to the text content (and metadata) of an email message.
    Each Post can have zero or more Attachments.

    Attributes:
        USER_AGENT_LENGTH: The maximum size of the user_agent column.
    """

    USER_AGENT_LENGTH = 255

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    sender_id = db.Column(
        db.Integer, db.ForeignKey('sender.id', ondelete='CASCADE'),
        nullable=False, index=True)
    created_utc = db.Column(db.UTCDateTime, nullable=False, server_default=db.func.now(6))
    caption = db.Column(db.UnicodeText, nullable=False)
    user_agent = db.Column(db.Unicode(length=USER_AGENT_LENGTH), nullable=True)
    is_barked = db.Column(db.Boolean, nullable=False, default=False)

    sender = db.relationship(Sender, backref=db.backref('posts', cascade='all, delete-orphan'))

    @property
    def has_attachment(self):
        """
        Does this Post have at least one Attachment?

        Returns:
            Boolean True if an Attachment exists for this instance.
        """
        return len(self.attachments) > 0

    @property
    def top_attachment(self):
        """
        Return the "top" Attachment for this Post.

        In common usage each Post only has a single Attachment and this method
        doesn't do anything interesting. It's entirely possible, however, for a
        Post to have arbitrarily many Attachments. This method is used to
        whittle that set down to a single result for display contexts where only
        one Attachment should be seen.

        Note that the Post *must* have at least one Attachment for this method
        to succeed! The exact Attachment returned in cases where more than one
        exists is not currently well defined.

        Returns:
            Single instance of Attachment.
        """
        return self.attachments[0]

    def new_attachment(self, **kwargs):
        """
        Create a fresh Attachment instance connected to this Post.

        Does not require any arguments, however any kewyord args that are
        provided will be passed to the Attachment constructor.

        Returns:
            New Attachment instance.
        """
        from windowbox.models.attachment import Attachment

        kwargs['post'] = self

        return Attachment(**kwargs)

    def set_stripped_caption(self, caption):
        """
        Strip and sanitize the provided caption, then use its value.

        This method performs the following sanitizations:

          - Strips things that look like email signatures (delineated) by the
            first line containing nothing but dashes and whitespace.
          - Squashes runs of two or more successive newlines down to two.
          - Strips all leading and trailing whitespace.

        Once the sanitizations are done, the `caption` attribute is set.

        Args:
            caption: The unsanitized caption to set.
        """

        # Find the email signature and chop it off
        caption = SIGNATURE_MATCHER.split(caption)[0]

        # Find and squash excessive runs of newline characters
        caption = NEWLINE_RUN_MATCHER.sub('\n\n', caption)

        self.caption = caption.strip()
