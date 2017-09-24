from __future__ import absolute_import
from flask import make_response, render_template


class IndexView(object):
    MODE_SINCE = 'since'
    MODE_UNTIL = 'until'

    def __init__(self, items, has_next, mode):
        self.items = items
        self.has_next = has_next
        self.mode = mode

    def render_html(self):
        last_id = self.items[-1].id
        template_vars = {
            'items': self.items,
            'has_next': self.has_next,
            'since': last_id if self.mode == self.MODE_SINCE else None,
            'until': last_id if self.mode == self.MODE_UNTIL else None}

        return render_template('index_posts.html', **template_vars)

    def render_rss2(self):
        return self._render_xml('index_posts_rss2.xml', content_type='application/rss+xml')

    def render_atom(self):
        return self._render_xml('index_posts_atom.xml', content_type='application/atom+xml')

    def render_sitemap(self):
        return self._render_xml('index_posts_sitemap.xml', content_type='application/xml')

    def _render_xml(self, template_name, content_type):
        template_vars = {
            'items': self.items}

        body_xml = render_template(template_name, **template_vars)

        response = make_response(body_xml)
        response.headers['Content-Type'] = content_type

        return response
