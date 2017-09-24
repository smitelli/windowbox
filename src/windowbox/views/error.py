from __future__ import absolute_import
from flask import render_template


class ErrorView(object):
    def __init__(self, error, stack=None):
        self.error = error
        self.stack = stack

    def render_html(self):
        template_vars = {
            'error': self.error,
            'stack': self.stack}

        return render_template('error.html', **template_vars)
