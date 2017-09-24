from __future__ import absolute_import
from flask import jsonify
from windowbox.handlers import get_or_404
from windowbox.models.post import PostManager
from windowbox.views.page import PageView
from windowbox.views.single import SingleView


class PostHandler(object):
    @classmethod
    def get(cls, post_id=None, as_json=False):
        render = cls._render_json if as_json else cls._render_html

        post = get_or_404(PostManager.get_by_id, post_id)
        attachment = get_or_404(post.get_attachment)
        metadata = attachment.get_metadata()
        previous, next = PostManager.get_adjacent_by_id(post_id)

        return render(post, attachment, metadata, previous, next)

    @staticmethod
    def _render_html(post, attachment, metadata, previous, next):
        view = SingleView(
            item=post, attachment=attachment, metadata=metadata,
            prev_item=previous, next_item=next)

        kwargs = {
            'title': post.get_message(length=50),
            'head_extra': view.render_head_extra(),
            'body': view.render_html()}

        return PageView(**kwargs).render_html()

    @staticmethod
    def _render_json(post, attachment, metadata, previous, next):
        data = {
            'post': post.to_dict(),
            'previous_id': previous.id if previous else None,
            'next_id': next.id if next else None}

        data['post']['attachment'] = attachment.to_dict()
        data['post']['attachment']['metadata'] = metadata.to_dict()

        return jsonify(**data)
