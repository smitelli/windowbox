"""
Wrapper client for the Tweepy library, intended for simple tweeting.

Attributes:
    logger: Logger instance scoped to the current module name.
"""
import logging
import tweepy

logger = logging.getLogger(__name__)


class TwitterClient:
    """
    Twitter API Client.
    """

    def __init__(
            self, consumer_key, consumer_secret, access_token,
            access_token_secret, status_length=280, url_length=23, timeout=10):
        """
        Constructor.

        Args:
            consumer_key: OAuth consumer key.
            consumer_secret: OAuth consumer secret.
            access_token: OAuth access token/key.
            access_token_secret: OAuth access token secret.
            status_length: Maximum length of status text accepted by the API at
                this time.
            url_length: Length of embedded short URLs at this time.
            timeout: Optional number of seconds to wait for a response from the
                API server.
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.status_length = status_length
        self.url_length = url_length
        self.timeout = timeout

        self.client = None

    def _make_client(self):
        """
        Create and return a Tweepy client using the current instance attributes.

        Returns:
            Instance of tweepy.api.API, fully configured.
        """
        logger.debug('Creating Twitter API client instance')

        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)

        return tweepy.API(auth, timeout=self.timeout)

    def update_status(self, status_text):
        """
        Post `status_text` as a tweet.

        Args:
            status_text: Tweet text to send to Twitter.

        Returns:
            Instance of tweepy.models.Status in the case of success.
        """
        if self.client is None:
            self.client = self._make_client()

        logger.debug('Sending tweet to Twitter...')
        response = self.client.update_status(
            status=status_text, enable_dmcommands=False)
        logger.debug('...done')

        return response
