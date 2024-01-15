from ._abstract import AbstractScraper
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import Union, List
import numpy as np


class PlayerDataScraper(AbstractScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.basketball-reference.com/players/"

    def _get_players_html(self, letter: str):
        url = f"{self.base_url}{letter}/"
        players = self.rate_limited_request(url)
        soup = BeautifulSoup(players.content, "html.parser")

        if soup.find('h1').text == 'Page Not Found (404 error)':
            return False
        else:
            return soup

    def _scrape_letter(self, first_letter: str):
        try:
            players_df = pd.read_html(
                str(self._get_players_html(first_letter).find_all('table', id='players')[0]))[0]
            self.scrape_logger.info(
                f'Scraped letter {first_letter} | {len(players_df)} players')
            players_df = players_df.set_index('Player').reset_index()
            return players_df

        except Exception as e:
            self.scrape_logger.error(
                f'Failed to scrape letter {first_letter}: {e}\n')
            return None

    def scrape(self, first_letter: Union[str, List[str]]):
        if isinstance(first_letter, str):
            first_letter = [first_letter]

        self.player_failed_letters = []
        players_df = pd.DataFrame()
        self.player_scraping_lag_time = 0
        start_time = time.time()

        self.scrape_logger.warning(
            '\n\n\n-------------------------------------Start of Scraping Player Info!-------------------------------------\n\n\n')

        for element in first_letter:
            self._scrape_letter(letter=element)
            self.scrape_logger.info(
                f"Scraping players data for letter {element}")
            loop_players_df = self._scrape_letter(element)

            if loop_players_df is None:
                self.player_failed_letters.append(element)
                continue

            players_df = pd.concat([loop_players_df, players_df], axis=0)
            self.scrape_logger.info(
                f'Concatenated letter {element} | {len(players_df)} players')

            # Add a lag time between requests
            lag = np.random.randint(4, 6)
            self.player_scraping_lag_time += lag
            self.scrape_logger.info(f'Cycle lag time: {lag}')
            time.sleep(lag)

        players_df = players_df.set_index('Player').reset_index()

        self.scrape_logger.info(
            f'Total lag time: {self.player_scraping_lag_time} seconds | {round(self.player_scraping_lag_time / 60, 2)} minutes | {round(self.player_scraping_lag_time / 3600, 2)} hours')
        self.scrape_logger.info(
            f'Failed letters: {len(self.player_failed_letters)} out of {len(first_letter)} letters')
        self.scrape_logger.info(
            f'Time elapsed: {time.time() - start_time} seconds | {round((time.time() - start_time) / 60, 2)} minutes | {round((time.time() - start_time) / 3600, 2)} hours')
        self.scrape_logger.info(
            f'Averaged {round((time.time() - start_time) / len(first_letter), 2)} seconds per letter')
        self.scrape_logger.warning(
            '\n\n\n-------------------------------------End of Scraping Player Info!-------------------------------------\n\n\n')


class GameDataScraper(AbstractScraper):
    def __init__(self):
        self.base_url = "https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html#schedule"

    def scrape(self, year: str, month: str, day: str, team: str):
        # Implementation for scraping game data
        print(f"Scraping game data for {year}-{month}-{day} for team {team}")
        # Add your scraping logic here
