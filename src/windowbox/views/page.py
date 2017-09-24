from __future__ import absolute_import
from flask import Markup, render_template


class PageView(object):
    def __init__(self, title, body, head_extra=None):
        self.title = title
        self.body = body
        self.head_extra = head_extra

    def render_html(self):
        template_vars = {
            'page_title': self.title,
            'page_body': Markup(self.body),
            'head_extra': Markup(self.head_extra) if self.head_extra else None}

        return render_template('page.html', **template_vars)
