from flask import render_template, make_response


class IndexView(object):
    def __init__(self, items, has_next):
        self.items = items
        self.has_next = has_next

    def render_html(self):
        template_vars = {
            'items': self.items,
            'has_next': self.has_next,
            'last_id': self.items[-1].id}

        return render_template('index_posts.html', **template_vars)

    def render_rss2(self):
        return self._render_xml(format='rss2')

    def render_atom(self):
        return self._render_xml(format='atom')

    def _render_xml(self, format):
        template_name, content_type = {
            'rss2': ('index_posts_rss2.xml', 'application/rss+xml'),
            'atom': ('index_posts_atom.xml', 'application/atom+xml')
        }[format]

        template_vars = {
            'items': self.items}

        body_xml = render_template(template_name, **template_vars)

        response = make_response(body_xml)
        response.headers['Content-Type'] = content_type

        return response
