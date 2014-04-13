from flask import render_template


class IndexView(object):
    def __init__(self, items, has_next):
        self.items = items
        self.has_next = has_next

    def render_html(self):
        template_vars = {
            'items': self.items,
            'has_next': self.has_next,
            'last_id': self.items[-1].id}

        return render_template('index_posts.html', **template_vars)
