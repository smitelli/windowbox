from flask import render_template


class ErrorView(object):
    def __init__(self, title=None, code=500):
        self.title = title
        self.code = code

    def render_html(self):
        template_vars = {
            'title': self.title,
            'code': self.code}

        return render_template('error.html', **template_vars)
