# Built-in Libraries
import requests
import logging
from abc import ABC, abstractmethod
import time

# Third-party Libraries
from ratelimit import limits, sleep_and_retry

# Internal Imports
from nba_data_scraper.utils._logger import Logger


class AbstractScraper(ABC):
    def __init__(self):
        self.scrape_logger = Logger().scrape_logger

    # Adjust the rate limit as per the website's policy 20req/60sec
    @sleep_and_retry
    @limits(calls=20, period=60)
    def rate_limited_request(self, url: str, headers: dict = None, max_retries: int = 2):
        """Rate limited request to the website. (20 requests/min)

        Args:
            url (str): URL to retrieve data from
            headers (dict, optional): Headers to be used for API calls. Defaults to None.
            max_retries (int, optional): Maximum number of retries. Defaults to 3.

        Returns:
            response: Response from API call
        """
        for i in range(max_retries):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                self.scrape_logger.info(
                    f'Request successful at URL: {url}')
                return response
            except requests.HTTPError as http_err:
                self.scrape_logger.error(f'HTTP error occurred: {http_err}')
            except Exception as err:
                self.scrape_logger.error(f'Other error occurred: {err}')
            time.sleep(2**i)

        raise Exception(
            f'Maximum number of retries reached at URL: {url}')

    @abstractmethod
    def scrape(self, *args, **kwargs):
        """Abstract method for scraping data. To be implemented by concrete classes."""
        pass
