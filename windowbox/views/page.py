from __future__ import absolute_import
from datetime import datetime
from flask import Markup, render_template


class PageView(object):
    def __init__(self, title, body):
        self.title = title
        self.body = body

    def render_html(self):
        template_vars = {
            'page_title': self.title,
            'page_body': Markup(self.body),
            'copyright_year': datetime.now().year}

        return render_template('page.html', **template_vars)
