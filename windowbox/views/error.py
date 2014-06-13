from __future__ import absolute_import
from flask import render_template


class ErrorView(object):
    def __init__(self, error, title=None):
        self.error = error

    def render_html(self):
        template_vars = {
            'error': self.error}

        return render_template('error.html', **template_vars)
