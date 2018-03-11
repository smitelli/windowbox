from __future__ import absolute_import
from flask import Markup, render_template
from windowbox.views.metadata import MetadataView


class SingleView(object):
    def __init__(self, item, attachment, metadata, prev_item=None, next_item=None):
        self.item = item
        self.attachment = attachment
        self.metadata = metadata
        self.prev_item = prev_item
        self.next_item = next_item

    def render_html(self):
        metadata_html = MetadataView(self.metadata).render_html()

        template_vars = {
            'item': self.item,
            'attachment': self.attachment,
            'metadata': Markup(metadata_html),
            'prev_item': self.prev_item,
            'next_item': self.next_item}

        return render_template('single_post.html', **template_vars)

    def render_head_extra(self):
        template_vars = {
            'item': self.item,
            'attachment': self.attachment}

        return render_template('single_post_head.html', **template_vars)