from flask import render_template


class IndexView(object):
    def __init__(self, items):
        self.items = items

    def render_html(self):
        template_vars = {
            'items': self.items}

        return render_template('index_posts.html', **template_vars)
