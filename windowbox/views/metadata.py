from flask import render_template


class MetadataView(object):
    def __init__(self, metadata):
        self.metadata = metadata

    def render_html(self):
        template_vars = {}

        return render_template('metadata.html', **template_vars)
