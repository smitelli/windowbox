"""
Bare-bones API client for Google Maps.

Attributes:
    logger: Logger instance scoped to the current module name.
"""

import logging
import requests

logger = logging.getLogger(__name__)


class GMAPIClientError(Exception):
    """
    Base exception class for any error that occurs within this client code.
    """
    pass


class GoogleMapsAPIClient:
    """
    Google Maps API Client.

    Attributes:
        GEOCODE_URL: URL/endpoint to use in geocode lookups.
    """

    GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

    def __init__(self, *, api_key, timeout=10):
        """
        Constructor.

        Args:
            api_key: Key to authenticate with when communicating with Google.
            timeout: Optional number of seconds to wait for a response from the
                API server before giving up.
        """
        self.api_key = api_key
        self.timeout = timeout

    def latlng_to_address(self, *, latitude, longitude):
        """
        Convert a latitude/longitude pair into a formatted address.

        This uses the Google Maps API to perform the lookup. Due to the fact
        that Google is scary accurate at this and many coordinate pairs are
        captured in private locations, the result set is searched until an
        "approximate" match is found. This should not have any speficic info.

        Args:
            latitude: Number in the range -90 (south) to 90 (north).
            longitude: Number in the range -180 (west) to 180 (east).

        Returns:
            String representation of the address at the specified point.

        Raises:
            GMAPIClientError: The response from the API server was either not
                successful or did not contain enough information to locate the
                address.
        """
        logger.debug(f'GET {self.GEOCODE_URL}?<redacted>...')

        response = requests.get(
            self.GEOCODE_URL,
            params={'key': self.api_key, 'latlng': f'{latitude},{longitude}'},
            timeout=self.timeout)
        response.raise_for_status()
        response_data = response.json()

        logger.debug(f'...status is {response_data["status"]}')

        if response_data['status'] != 'OK':
            raise GMAPIClientError(f'got unexpected status: {response_data["status"]}')

        try:
            approx_match = next(filter(
                lambda r: r['geometry']['location_type'] == 'APPROXIMATE',
                response_data['results']))
        except StopIteration:
            raise GMAPIClientError(f'could not find an "approximate" location type')

        return approx_match['formatted_address']
