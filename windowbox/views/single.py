from flask import render_template
from windowbox.views.metadata import MetadataView


class SingleView(object):
    def __init__(self, item, prev_item=None, next_item=None):
        self.item = item
        self.prev_item = prev_item
        self.next_item = next_item

    def render_html(self):
        attachment = self.item.get_attachment()
        metadata = MetadataView(attachment)

        template_vars = {
            'item': self.item,
            'attachment': attachment,
            'metadata': metadata.render_html(),
            'prev_item': self.prev_item,
            'next_item': self.next_item}

        return render_template('single_post.html', **template_vars)
