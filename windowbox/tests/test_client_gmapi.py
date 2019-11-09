"""
Tests for the Google Maps API client.
"""

import pytest
from unittest.mock import Mock, patch
from windowbox.clients.gmapi import GoogleMapsAPIClient, GMAPIClientError


@pytest.fixture
def gmapi():
    """
    Return a Google Maps API client.
    """
    return GoogleMapsAPIClient(api_key='secrets4google', timeout=15)


def test_constructor(gmapi):
    """
    Should accept and store all publicly-defined attributes.
    """
    assert gmapi.api_key == 'secrets4google'
    assert gmapi.timeout == 15


def test_latlng_to_address(gmapi):
    """
    Should send latitude/longitude pairs to the API and parse the response.
    """
    response = Mock()
    response.json.return_value = {
        'status': 'OK',
        'results': [
            {
                'formatted_address': 'not this one',
                'geometry': {'location_type': 'ROOFTOP'}
            },
            {
                'formatted_address': 'not this one either',
                'geometry': {'location_type': 'RANGE_INTERPOLATED'}
            },
            {
                'formatted_address': 'getting warmer',
                'geometry': {'location_type': 'GEOMETRIC_CENTER'}
            },
            {
                'formatted_address': 'Bingo, NC, USA',
                'geometry': {'location_type': 'APPROXIMATE'}
            },
            {
                'formatted_address': 'too far',
                'geometry': {'location_type': 'APPROXIMATE'}
            }
        ]
    }

    with patch('requests.get', return_value=response) as mock_get:
        address = gmapi.latlng_to_address(latitude=36, longitude=-78.9)
        mock_get.assert_called_once_with(
            'https://maps.googleapis.com/maps/api/geocode/json',
            params={'key': 'secrets4google', 'latlng': '36,-78.9'},
            timeout=15)
        assert address == 'Bingo, NC, USA'


def test_latlng_to_address_status(gmapi):
    """
    Should detect and raise on bad status.
    """
    response = Mock()
    response.json.return_value = {'status': 'WHOA_NELLY'}

    with patch('requests.get', return_value=response):
        with pytest.raises(GMAPIClientError, match='got unexpected status: WHOA_NELLY'):
            gmapi.latlng_to_address(latitude=36, longitude=-78.9)


def test_latlng_to_address_resolution(gmapi):
    """
    If it can't find an APPROXIMATE result, don't succeed.
    """
    response = Mock()
    response.json.return_value = {
        'status': 'OK',
        'results': [
            {
                'formatted_address': 'nope',
                'geometry': {'location_type': 'ROOFTOP'}
            },
            {
                'formatted_address': 'wrong',
                'geometry': {'location_type': 'RANGE_INTERPOLATED'}
            },
            {
                'formatted_address': 'negative',
                'geometry': {'location_type': 'GEOMETRIC_CENTER'}
            }
        ]
    }

    with patch('requests.get', return_value=response):
        with pytest.raises(GMAPIClientError, match='could not find an "approximate" location type'):
            gmapi.latlng_to_address(latitude=36, longitude=-78.9)
