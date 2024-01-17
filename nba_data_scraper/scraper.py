# Built-in Libraries
import datetime as dt
from typing import List, Union

# Third-party Libraries
from pandas import DataFrame

# Internal Imports
from ._constants import MONTHS, TEAM_ABBS
from ._data_scraper import PlayerDataScraper, ScheduleDataScraper, GameDataScraper


class NBAScraper:
    def __init__(self,):
        self.player_scraper = PlayerDataScraper()
        self.schedule_scraper = ScheduleDataScraper()
        self.game_scraper = GameDataScraper()
        self._all_letters = None
        self._teams = None
        self.months = MONTHS
        self._player_failed_letters = None
        self._schedule_failed_dates = None
        self._games_failed_game_ids = None
        self._schedule_df = None
        self._shots_from_games = None

    @property
    def all_letters(self):
        if not self._all_letters:
            self._all_letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        return self._all_letters

    @property
    def teams(self):
        if not self._teams:
            self._teams = TEAM_ABBS
        return self._teams

    @property
    def player_failed_letters(self):
        try:
            if self._player_failed_letters is None:
                return self.player_scraper.player_failed_letters
        except AttributeError:
            raise AttributeError(
                'Please scrape player data before accessing this property.')

    @property
    def schedule_failed_dates(self):
        try:
            if self._schedule_failed_dates is None:
                return self.schedule_scraper.failed_dates
        except AttributeError:
            raise AttributeError(
                'Please scrape schedule data before accessing this property.')

    @property
    def games_failed_game_ids(self):
        try:
            if self._games_failed_game_ids is None:
                return self.game_scraper.failed_games
        except AttributeError:
            raise AttributeError(
                'Please scrape game data before accessing this property.')

    @property
    def schedule_df(self):
        if self._schedule_df is None:
            raise AttributeError(
                'Please scrape schedule data before accessing this property.')
        else:
            return self._schedule_df

    @property
    def shots_from_games(self):
        if self._shots_from_games is None:
            raise AttributeError(
                'Please scrape game data before accessing this property.')
        else:
            return self._shots_from_games

    def scrape_player_data(self, letter: Union[str, List[str]] = None):
        """Scrape player data from basketball-reference.com.

        Args:
            letter: input letter or list of letters in string format, e.g. 'a' or ['a','b'].

        Returns:
            pd.DataFrame: Pandas DataFrame containing player data.
        """
        return self.player_scraper.scrape(letter)

    def scrape_all_player_data(self):
        """Scrape all player data from basketball-reference.com.

        Returns:
            pd.DataFrame: Pandas DataFrame containing player data.
        """
        return self.player_scraper.scrape(self.all_letters)

    def scrape_schedule_data(self, year: Union[str, List[str]] = None, month: Union[str, List[str]] = None):
        """Scrape schedule data from basketball-reference.com

        Args:
            year: input year or list of years in string format yyyy, e.g. '2023' or ['2022', '2023'].
            month: input month or list of months in en-US full month name format, e.g. 'october'.

        Returns:
            pd.DataFrame: Pandas DataFrame containing schedule data.
        """
        self._schedule_df = self.schedule_scraper.scrape(year, month)
        return self._schedule_df

    def scrape_all_schedule_data(self, start_year: int = 2000, end_year: int = dt.date.today().year):
        """Scrape all schedule data from basketball-reference.com starting from the year 2000

        Returns:
            pd.DataFrame: Pandas DataFrame containing schedule data.
        """
        years = [str(i) for i in range(start_year, end_year + 1)]
        self._schedule_df = self.schedule_scraper.scrape(
            year=years, month=self.months)
        return self._schedule_df

    def scrape_game_data(self, schedule_df: DataFrame = None):
        """Scrape shots data from each game from basketball-reference.com

        Args:
            schedule_df: Schedule DataFrame. Use the scrape_schedule_data method to get this DataFrame.

        Returns:
            pd.DataFrame: Pandas DataFrame containing shots data.
        """
        schedule_df = schedule_df if schedule_df is not None else self._schedule_df

        if schedule_df is None:
            raise ValueError(
                'Please provide a schedule DataFrame to scrape game data. Use the scrape_schedule_data method to get this DataFrame.')

        self._shots_from_games = self.game_scraper.scrape(
            schedule_df=schedule_df)

        return self._shots_from_games
