"""
Post controller.

Attributes:
    PostSet: namedtuple that wraps "single Post" responses. Includes the
        requested Post, as well as (potentially) the immediate adjacent older
        and newer Posts.
    ManyPostSet: namedtuple that wraps "many Post" responses. In addition to a
        list of Posts, also contains information needed to build pagination.
"""

import enum
import sqlalchemy.orm.exc
from collections import namedtuple
from datetime import datetime, timezone
from windowbox.controllers import BaseController
from windowbox.models.post import Post
from windowbox.models.sender import Sender

PostSet = namedtuple('PostSet', ['post', 'older_post', 'newer_post'])
ManyPostSet = namedtuple('ManyPostSet', ['posts', 'has_more', 'page_mode'])


class PostController(BaseController):
    """
    Post controller.

    Responsible for creation and lookup of Post models.

    Attributes:
        SITE_DEFAULT_LIMIT: The number of Posts to get by default.
        API_DEFAULT_LIMIT: The number of Posts to get by default in the REST API
            context.
        ATOM_LIMIT: The number of Posts to get when viewing Atom feeds.
        RSS_LIMIT: The number of Posts to get when viewing RSS feeds.
        MAX_LIMIT: The maximum acceptable limit on API requests.
    """

    SITE_DEFAULT_LIMIT = 9
    API_DEFAULT_LIMIT = 20
    ATOM_LIMIT = 30
    RSS_LIMIT = 30
    MAX_LIMIT = 100

    class UnknownSender(BaseController.ControllerError):
        """
        Indicates a message from a presently-unknown Sender.
        """
        pass

    @enum.unique
    class PAGE_MODE(enum.Enum):
        """
        The enumerated set of implemented pagination modes.

        Attributes:
            SINCE: Pages are moving "forward" in time and showing items that are
                "newer" than the ones on prior pages.
            UNTIL: Pages are moving "backward" in time and showing items that
                are "older" than the ones on prior pages.
        """
        SINCE = enum.auto()
        UNTIL = enum.auto()

    @classmethod
    def message_to_post(cls, message):
        """
        Build a Post model from an IMAP message.

        The "From" address of each message *must* match an existing Sender in
        the database. If this is not the case, this method will raise without
        creating a new Post. This is to avoid blithely publishing spam messages.

        Args:
            message: An message instance as returned by the IMAP client.

        Returns:
            Fresh Post instance built from the message content.

        Raises:
            UnknownSender: The message is from an unknown address.
        """
        try:
            sender = Sender.query.filter_by(email_address=message.from_address).one()
        except sqlalchemy.orm.exc.NoResultFound as exc:
            raise cls.UnknownSender from exc

        post = Post(
            sender=sender,
            created_utc=message.date,
            user_agent=message.x_mailer)
        post.set_stripped_caption(message.text_plain)

        return post

    @classmethod
    def get_by_id(cls, post_id, *, include_adjacent=True):
        """
        Return one Post model and its nearest adjacent siblings from an ID.

        Args:
            post_id: The primary key of a Post to get.
            include_adjacent: If True (the default) also query for the two Posts
                that are stored immediately adjacent to the requested one.

        Returns:
            PostSet namedtuple with a Post instance matching the provided
            argument, as well as Post instance(s) for older/newer Post instances
            if they exist and are desired.

        Raises:
            NoResultFound: The provided ID didn't match any known Posts.
        """
        try:
            post = Post.query.filter_by(id=post_id).one()
        except sqlalchemy.orm.exc.NoResultFound as exc:
            raise cls.NoResultFound from exc

        older = None
        newer = None
        if include_adjacent:
            older = Post.query.filter(Post.id < post_id).order_by(Post.id.desc()).first()
            newer = Post.query.filter(Post.id > post_id).order_by(Post.id.asc()).first()

        return PostSet(post=post, older_post=older, newer_post=newer)

    @classmethod
    def parse_query_args(cls, *, since_id, until_id, limit):
        """
        Query string parser/validator for get_many().

        Args:
            Same as get_many().

        Returns:
            Dict containing parsed values for since_id, until_id, and limit.

        Raises:
            InvalidArgument: One of the provided values was not an integer or
                otherwise usable.
        """
        try:
            since_id = int(since_id) if (since_id is not None) else None
            until_id = int(until_id) if (until_id is not None) else None
            limit = int(limit) if (limit is not None) else None
        except ValueError as exc:
            raise cls.InvalidArgument from exc

        # Requesting both `since` and `until` is not supported
        if since_id is not None and until_id is not None:
            raise cls.InvalidArgument

        # If there is a limit, it must be within the specified ranges
        if (limit is not None) and not (1 <= limit <= cls.MAX_LIMIT):
            raise cls.InvalidArgument

        return {
            'since_id': since_id,
            'until_id': until_id,
            'limit': limit}

    @classmethod
    def get_many(cls, *, since_id=None, until_id=None, limit=None):
        """
        Return several Post models matching the filter criteria.

        By default, Posts are returned in descending (newest-first) order. If
        `since_id` is set, the order is reversed to ascending order starting
        with the first newer item than the provided ID.

        If `until_id` is set, no Posts equal to or greater than that ID (i.e. no
        newer items) will be returned.

        If `limit` is set, no more than that many Posts will be returned in a
        single call. There may be fewer items returned on the last page. There
        is a default value if unspecified; if all items are desired, explicitly
        set this to None.

        Args:
            since_id: If set, switches the order to newest-first and skips any
                Posts with an equal or smaller ID.
            until_id: If set, skips any Posts with an equal or larger ID.
            limit: If set to an integer, sets the maximum number of items that
                can be returned. If None, there is no limit.

        Returns:
            ManyPostSet tuple with the matching Post instances and the
            pagination flags.
        """
        args = cls.parse_query_args(
            since_id=since_id, until_id=until_id, limit=limit)

        q = Post.query

        if args['since_id'] is not None:
            q = q.order_by(Post.id.asc()).filter(Post.id > args['since_id'])
            page_mode = cls.PAGE_MODE.SINCE
        else:
            q = q.order_by(Post.id.desc())
            page_mode = cls.PAGE_MODE.UNTIL

        if args['until_id'] is not None:
            q = q.filter(Post.id < args['until_id'])

        if args['limit'] is not None:
            # Query for one extra item, check if it's present, then discard it.
            posts = q.limit(args['limit'] + 1).all()
            has_more = (len(posts) > args['limit'])
            posts = posts[:args['limit']]
        else:
            # All items were requested at once; there can't be more pages.
            posts = q.all()
            has_more = False

        return ManyPostSet(posts=posts, has_more=has_more, page_mode=page_mode)

    @staticmethod
    def get_lastmod_datetime():
        """
        Return the date of the most recent Post.

        If there are no Posts yet defined, the returned date is "now."

        Returns:
            Python datetime object, representing the time of the most recent
            Post, or "now" if no Posts yet exist.
        """
        try:
            newest_post = Post.query.order_by(Post.id.desc()).limit(1).one()
            lastmod = newest_post.created_utc
        except sqlalchemy.orm.exc.NoResultFound:
            lastmod = datetime.now(tz=timezone.utc)

        return lastmod

    @staticmethod
    def yield_all():
        """
        Return all Posts in the database in descending order.

        This is written as a generator to avoid the overhead of constructing a
        list of all instances up-front.

        Yields:
            All known Post instances.
        """
        yield from Post.query.order_by(Post.id.desc())

    @staticmethod
    def yield_unbarked():
        """
        Return all "unbarked" Posts in ascending order.

        This is written as a generator to avoid the overhead of constructing a
        list of all instances up-front.

        Yields:
            All matching Post instances.
        """
        yield from Post.query.filter_by(is_barked=False).order_by(Post.id.asc())
