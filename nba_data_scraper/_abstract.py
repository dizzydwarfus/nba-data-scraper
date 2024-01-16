from ratelimit import limits, sleep_and_retry
import requests
import logging
from abc import ABC, abstractmethod
from nba_data_scraper.utils._logger import Logger


class AbstractScraper(ABC):
    def __init__(self):
        self.scrape_logger = Logger().scrape_logger

    @sleep_and_retry
    # Adjust the rate limit as per the website's policy 20req/60sec
    @limits(calls=20, period=60)
    def rate_limited_request(self, url: str, headers: dict = None):
        """Rate limited request to the website. (20 requests/min)

        Args:
            url (str): URL to retrieve data from
            headers (dict, optional): Headers to be used for API calls. Defaults to None.

        Returns:
            response: Response from API call
        """
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.scrape_logger.error(f'Request failed at URL: {url}')
        else:
            self.scrape_logger.info(f'Request successful at URL: {url}')
        return response

    @abstractmethod
    def scrape(self, *args, **kwargs):
        """Abstract method for scraping data. To be implemented by concrete classes."""
        pass
