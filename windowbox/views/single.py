from flask import render_template


class SingleView(object):
    def __init__(self, item, prev_item=None, next_item=None):
        self.item = item
        self.prev_item = prev_item
        self.next_item = next_item

    def render_html(self):
        template_vars = {
            'item': self.item,
            'prev_item': self.prev_item,
            'next_item': self.next_item}

        return render_template('single_post.html', **template_vars)
