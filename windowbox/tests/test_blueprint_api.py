"""
Integration tests for the API blueprint (and its schemas).
"""


def assert_json_200(res):
    """
    Verify a response looks like a JSON payload.
    """
    assert res.status_code == 200
    assert res.content_type == 'application/json'


def assert_json_404(res):
    """
    Verify a response looks like a JSON payload with a 404 error.
    """
    assert res.status_code == 404
    assert res.content_type == 'application/json'
    assert res.json == {
        'error': {
            'details': 'The requested URL was not found on the server. If you '
            'entered the URL manually please check your spelling and try again.',
            'message': 'Not Found',
            'status': 404}}


def assert_json_422(res):
    """
    Verify a response looks like a JSON payload with a 422 error.
    """
    assert res.status_code == 422
    assert res.content_type == 'application/json'
    assert res.json == {
        'error': {
            'details': 'The request was well-formed but was unable to be '
            'followed due to semantic errors.',
            'message': 'Unprocessable Entity',
            'status': 422}}


def test_api_get_many_posts(client, post_instances):
    """
    Test "get many Posts" endpoint.
    """
    res = client.get('/api/posts?limit=10')

    assert_json_200(res)
    assert len(res.json['posts']) == 10
    assert res.json['posts'][0]['id'] == 12
    assert res.json['posts'][9]['id'] == 3
    assert res.json['more_url'] is not None

    res = client.get('/api/posts?until=3&limit=10')

    assert_json_200(res)
    assert len(res.json['posts']) == 2
    assert res.json['posts'][0]['id'] == 2
    assert res.json['posts'][1]['id'] == 1
    assert res.json['more_url'] is None

    res = client.get('/api/posts?since=0&limit=10')

    assert_json_200(res)
    assert len(res.json['posts']) == 10
    assert res.json['posts'][0]['id'] == 1
    assert res.json['posts'][9]['id'] == 10
    assert res.json['more_url'] is not None

    res = client.get('/api/posts?since=10&limit=10')

    assert_json_200(res)
    assert len(res.json['posts']) == 2
    assert res.json['posts'][0]['id'] == 11
    assert res.json['posts'][1]['id'] == 12
    assert res.json['more_url'] is None

    res = client.get('/api/posts?until=buggin')

    assert_json_422(res)


def test_api_get_post(client, post_instances):
    """
    Test "get one Post" endpoint.
    """
    res = client.get('/api/posts/1')

    assert_json_200(res)
    assert res.json['post']['id'] == 1
    assert res.json['older_url'] is None
    assert res.json['newer_url'] is not None

    res = client.get('/api/posts/12')

    assert_json_200(res)
    assert res.json['post']['id'] == 12
    assert res.json['older_url'] is not None
    assert res.json['newer_url'] is None

    res = client.get('/api/posts/6')

    assert_json_200(res)
    assert res.json['post']['id'] == 6
    assert res.json['older_url'] is not None
    assert res.json['newer_url'] is not None

    res = client.get('/api/posts/666666')

    assert_json_404(res)


def test_attachment_get_attachment(client, post_instances):
    """
    Test "get one Attachment/Derivative" endpoint.
    """
    res = client.get('/api/attachments/1')

    assert_json_200(res)
    assert res.json['attachment']['id'] == 1

    res = client.get('/api/attachments/666666')

    assert_json_404(res)
