from __future__ import absolute_import
from flask import render_template


class ErrorView(object):
    def __init__(self, error, title=None):
        self.error = error
        self.title = title

    def render_html(self):
        template_vars = {
            'error': self.error,
            'title': self.title}

        return render_template('error.html', **template_vars)
