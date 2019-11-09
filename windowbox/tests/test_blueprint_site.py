"""
Integration tests for the site blueprint.
"""


def assert_html_200(res):
    """
    Verify a response looks like an HTML page.
    """
    assert res.status_code == 200
    assert res.content_type == 'text/html; charset=utf-8'


def assert_html_404(res):
    """
    Verify a response looks like an HTML page with a 404 error on it.
    """
    assert res.status_code == 404
    assert res.content_type == 'text/html; charset=utf-8'
    assert b'Not Found' in res.data
    assert b"Whatever you're looking for isn't here. Sorry about that." in res.data


def assert_html_422(res):
    """
    Verify a response looks like an HTML page with a 422 error on it.
    """
    assert res.status_code == 422
    assert res.content_type == 'text/html; charset=utf-8'
    assert b'Unprocessable Entity' in res.data
    assert (
        b'The request was well-formed but was unable to be followed due to '
        b'semantic errors.') in res.data


def assert_xml_200(res):
    """
    Verify a response looks like an XML document.
    """
    assert res.status_code == 200
    assert res.content_type == 'application/xml; charset=utf-8'


def test_site_get_index(client, post_instances):
    """
    Test index page.
    """
    res = client.get('/')

    assert_html_200(res)
    assert b'Post Fixture 12' in res.data
    assert b'Post Fixture 4' in res.data
    assert b'Post Fixture 3' not in res.data
    assert b'class="next-page"' in res.data

    res = client.get('/?until=4')

    assert_html_200(res)
    assert b'Post Fixture 4' not in res.data
    assert b'Post Fixture 3' in res.data
    assert b'Post Fixture 1' in res.data
    assert b'class="next-page"' not in res.data

    res = client.get('/?since=0')

    assert_html_200(res)
    assert b'Post Fixture 1' in res.data
    assert b'Post Fixture 9' in res.data
    assert b'Post Fixture 10' not in res.data
    assert b'class="next-page"' in res.data

    res = client.get('/?since=9')

    assert_html_200(res)
    assert b'Post Fixture 9' not in res.data
    assert b'Post Fixture 10' in res.data
    assert b'Post Fixture 12' in res.data
    assert b'class="next-page"' not in res.data

    res = client.get('/?until=buggin')

    assert_html_422(res)


def test_site_get_post(client, post_instances):
    """
    Test single Post pages.
    """
    res = client.get('/post/6')

    assert_html_200(res)
    assert b'Post Fixture 6' in res.data
    assert b'class="arrow newer"' in res.data
    assert b'class="arrow older"' in res.data

    res = client.get('/post/1')

    assert_html_200(res)
    assert b'Post Fixture 1' in res.data
    assert b'class="arrow newer"' in res.data
    assert b'class="arrow older"' not in res.data

    res = client.get('/post/12')

    assert_html_200(res)
    assert b'Post Fixture 12' in res.data
    assert b'class="arrow newer"' not in res.data
    assert b'class="arrow older"' in res.data

    res = client.get('/post/666666')

    assert_html_404(res)


def test_site_get_attachment_derivative(client, post_instances):
    """
    Test single Attachment/Derivative pages.
    """
    res = client.get('/attachment/1/300x300.png')

    assert res.status_code == 200
    assert res.content_type == 'image/png'
    assert res.content_length > 150  # a PNG is probably at least this big...
    assert res.headers.get('x-accel-redirect') is None

    client.application.config['USE_X_ACCEL_REDIRECT'] = True
    res = client.get('/attachment/1/300x300.png')

    assert res.status_code == 200
    assert res.content_type == 'image/png'
    assert res.content_length == 0
    assert res.headers.get('x-accel-redirect') is not None
    assert '//' not in res.headers.get('x-accel-redirect')

    res = client.get('/attachment/666666/300x300.png')

    assert_html_404(res)


def test_site_get_feed_atom(client, post_instances):
    """
    Test XML Atom feed.
    """
    res = client.get('/atom.xml')

    assert_xml_200(res)
    assert b'<updated>2018-12-01T00:00:00+00:00</updated>' in res.data
    assert b'<title>Post Fixture 1</title>' in res.data
    assert b'<title>Post Fixture 12</title>' in res.data


def test_site_get_feed_rss(client, post_instances):
    """
    Test XML RSS feed.
    """
    res = client.get('/rss.xml')

    assert_xml_200(res)
    assert b'<pubDate>Sat, 01 Dec 2018 00:00:00 +0000</pubDate>' in res.data
    assert b'<lastBuildDate>Sat, 01 Dec 2018 00:00:00 +0000</lastBuildDate>' in res.data
    assert b'<h1>Post Fixture 1</h1>' in res.data
    assert b'<h1>Post Fixture 12</h1>' in res.data


def test_site_get_feed_sitemap(client, post_instances):
    """
    Test XML sitemap feed.
    """
    res = client.get('/sitemap.xml')

    assert_xml_200(res)
    assert b'<lastmod>2018-12-01T00:00:00+00:00</lastmod>' in res.data
    assert b'/post/1</loc>' in res.data
    assert b'/post/12</loc>' in res.data


def test_site_get_health_check(client):
    """
    Test health check endpoint.
    """
    res = client.get('/health-check')

    assert res.status_code == 200
    assert res.content_type == 'text/plain; charset=utf-8'
    assert res.data == b'OK'
