from flask import render_template


class PageView(object):
    def __init__(self, title, body):
        self.title = title
        self.body = body

    def render_html(self):
        template_vars = {
            'page_title': self.title,
            'page_body': self.body}

        return render_template('page.html', **template_vars)