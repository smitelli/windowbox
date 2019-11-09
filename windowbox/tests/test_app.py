"""
Tests for the application.
"""

from datetime import datetime
from flask import make_response, render_template_string
from unittest.mock import patch
from windowbox import __version__ as windowbox_ver, prepare_response


def test_app(app):
    """
    Should have the expected initialized values.
    """
    assert app.name == 'windowbox'
    assert app.config['THIS_IS_A_TEST_FIXTURE'] == 'PASSED'


def test_prepare_response(app):
    """
    Responses should be appropriately modified.
    """
    with app.app_context():
        # Verify the custom headers
        res = prepare_response(make_response('test'))
        assert res.headers['x-george-carlin'] == 'I put a dollar in a change machine. Nothing changed.'

        # Verify the HTML minifier runs when it should
        with patch('windowbox.utils.minify_html', return_value='mini html') as mock_minify:
            res = prepare_response(
                make_response('test html', {'content-type': 'text/html'}))
            mock_minify.assert_called_once_with('test html')
            assert res.get_data(as_text=True) == 'mini html'

        # Verify the XML minifier runs when it should
        with patch('windowbox.utils.minify_xml', return_value='mini xml') as mock_minify:
            res = prepare_response(
                make_response('test xml', {'content-type': 'application/xml'}))
            mock_minify.assert_called_once_with('test xml', encoding=res.charset)
            assert res.get_data(as_text=True) == 'mini xml'


def test_not_found_error(client):
    """
    "Not Found" responses should dispatch to the correct blueprint.

    Since there is no nice way to mock the individual error handler functions,
    the "good enough" test is to just check the Content-Type and make a guess
    about which error handler it came from.
    """
    res = client.get('/not-a-page')
    assert res.content_type.startswith('text/html')

    res = client.get('/api/not-an-endpoint')
    assert res.content_type.startswith('application/json')


def test_template_globals(app):
    """
    Verify the template global variables and filters are all present.
    """
    with app.app_context():
        # Global variables
        assert render_template_string('{{ copyright_from }}') == '2004'
        assert render_template_string('{{ site_title }}') == 'Windowbox'
        assert render_template_string('{{ copyright_to }}') == str(datetime.now().year)
        assert render_template_string('{{ generator_version }}') == str(windowbox_ver)
        assert render_template_string('{{ generator_url }}')
        assert render_template_string('{{ tagline }}')

        # Filters
        with patch('windowbox.utils.datetime_to_rfc2822', return_value='rfc2822 date'):
            assert render_template_string('{{ dt|rfc2822format }}', dt='datetime') == 'rfc2822 date'
