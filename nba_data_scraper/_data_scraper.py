# Built-in Libraries
import re
import time
import datetime as dt
from typing import Union, List

# Third-party Libraries
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
import numpy as np

# Internal Imports
from ._constants import TEAM_ABBS
from ._abstract import AbstractScraper
from .utils._logger import Logger


class PlayerDataScraper(AbstractScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.basketball-reference.com/players/"
        self.scrape_logger = Logger(name='player_scraper_logger').scrape_logger

    def _get_players_html(self, letter: str):
        try:
            url = f"{self.base_url}{letter}/"
            players = self.rate_limited_request(url)
            soup = BeautifulSoup(players.content, "html.parser")
            return soup

        except Exception as e:
            raise ValueError(
                f'{e}')

    def _scrape_letter(self, letter: str):
        try:
            players_df = pd.read_html(
                str(self._get_players_html(letter).find_all('table', id='players')[0]))[0]
            self.scrape_logger.info(
                f'Scraped letter {letter} | {len(players_df)} players')
            players_df = players_df.set_index('Player').reset_index()
            return players_df

        except ValueError as err:
            self.scrape_logger.error(
                f'Failed to scrape letter {letter}: {err}')
            return None

        except Exception as err:
            self.scrape_logger.error(
                f'Failed to scrape letter {letter}: {err}')
            return None

    def scrape(self, letter: Union[str, List[str]]):
        """Scrape player data from basketball-reference.com.

        Args:
            letter (Union[str, List[str]]): input letter or list of letters in string format, e.g. 'a' or ['a','b'].

        Returns:
            pd.DataFrame: Pandas DataFrame containing player data.
        """
        if isinstance(letter, str):
            letter = [letter]

        if not letter:
            raise TypeError(
                f'Invalid input type of letter: {type(letter)}')

        self.player_failed_letters = []
        players_df = pd.DataFrame()
        start_time = time.time()

        self.scrape_logger.warning(
            '\n-------------------------------------Start of Scraping Player Info!-------------------------------------')

        for element in letter:
            loop_players_df = self._scrape_letter(element)

            if loop_players_df is None:
                self.player_failed_letters.append(element)
                continue

            players_df = pd.concat([loop_players_df, players_df], axis=0)
            self.scrape_logger.info(
                f'Concatenated letter {element} | {len(players_df)} players')

        if len(players_df) == 0:
            self.scrape_logger.error(
                f'No player data scraped. Please check your input parameters.')
            raise ValueError(
                f'No player data scraped. Please check your input parameters.')

        players_df = players_df.set_index('Player').reset_index()
        time_taken = time.time() - start_time

        self.scrape_logger.warning(
            '\n-------------------------------------End of Scraping Player Info!-------------------------------------')

        # Scraping Statistics
        self.scrape_logger.warning(
            '\n-------------------------------------Scraping Summary-------------------------------------')
        self.scrape_logger.info(
            f'Total players scraped: {len(players_df)}')
        self.scrape_logger.info(
            f'Failed letters: {len(self.player_failed_letters)} out of {len(letter)} letters')
        self.scrape_logger.info(
            f'Time elapsed: {time_taken} seconds | {round((time_taken) / 60, 2)} minutes | {round((time_taken) / 3600, 2)} hours')
        self.scrape_logger.info(
            f'Averaged {round((time_taken) / len(letter), 2)} seconds per letter\n------------------------------------------------------------------------------------------------------')

        return players_df


class ScheduleDataScraper(AbstractScraper):
    def __init__(self):
        self.base_url = "https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html#schedule"
        self.scrape_logger = Logger(name='game_scraper_logger').scrape_logger
        self.months = ['october', 'november', 'december', 'january', 'february',
                       'march', 'april', 'may', 'june', 'july', 'august', 'september']

    def _get_schedule_html(self, year: Union[str, int], month: str,):
        try:
            games = self.rate_limited_request(
                self.base_url.format(year=year, month=month))
            soup = BeautifulSoup(games.content, "html.parser")

            return soup

        except Exception as e:
            self.scrape_logger.error(
                f'Failed to scrape {year}-{month}: {e}\n')
            return None

    def _get_schedule_table(self, soup: BeautifulSoup,):
        try:
            df = pd.read_html(str(soup.find_all('table')))[
                0].drop(['Unnamed: 6',], axis=1)
            return df
        except:
            self.scrape_logger.error(
                f'Failed to get schedule table from BeautifulSoup object')
            return None

    def _process_daily_schedule(self, df: pd.DataFrame):
        try:
            df = df.loc[df['Date'] != 'Playoffs'].copy()
            df['DateTime'] = pd.to_datetime(
                df['Date'] + ' ' + df['Start (ET)'] + 'm', format='%a, %b %d, %Y %I:%M%p')
            df['DateStr'] = [dt.datetime.strftime(
                i, "%Y%m%d%H%M") for i in df['DateTime']]
            df = df.drop(['Date', 'Start (ET)', 'Notes'], axis=1)
            df.rename(columns={'Visitor/Neutral': 'Visitor', 'PTS': 'Visitor PTS', 'Home/Neutral': 'Home',
                               'PTS.1': 'Home PTS', 'Unnamed: 7': 'OT', 'Attend.': 'Attendance'}, inplace=True)
            df['Visitor_short'] = [TEAM_ABBS[name][0]
                                   for name in df['Visitor']]
            df['Home_short'] = [TEAM_ABBS[name][0] for name in df['Home']]
            df['game_id'] = df['DateStr'] + \
                df['Visitor_short'] + df['Home_short']
            df.set_index('DateTime', inplace=True)
            df['year'] = df.index.year
            df['month'] = df.index.month

            return df
        except Exception as e:
            self.scrape_logger.error(
                f'Failed to process daily schedule: {e}')
            return None

    def scrape(self, year: Union[str, List[str], int, List[int]], month: Union[str, List[str]],):
        """Scrape schedule data from basketball-reference.com

        Args:
            year (Union[str, List[str]]): input year or list of years in string or int format yyyy, e.g. '2023' or ['2022', '2023'].
            month (Union[str, List[str]]): input month or list of months in en-US full month name format, e.g. 'october'.

        Returns:
            pd.DataFrame: Pandas DataFrame containing schedule data.
        """
        if isinstance(year, str) or isinstance(year, int):
            year = [year]
        if isinstance(month, str):
            month = [month]

        pages_to_scrape = len(year) * len(month)
        start_time = time.time()
        schedule_df_list = []
        self.failed_dates = []
        self.scrape_logger.warning(
            '\n-------------------------------------Start of Scraping Schedule Info!-------------------------------------')
        for y in year:
            for m in month:
                self.scrape_logger.info(
                    f"Scraping schedule data for {y}-{m}")
                soup = self._get_schedule_html(year=y, month=m)

                if soup is None:
                    self.failed_dates.append(f'{y}-{m}')
                    continue

                df = self._get_schedule_table(soup)

                if df is None:
                    self.failed_dates.append(f'{y}-{m}')
                    continue

                df = self._process_daily_schedule(df)

                if df is None:
                    self.failed_dates.append(f'{y}-{m}')
                    continue

                schedule_df_list.append(df)

        if len(schedule_df_list) == 0:
            self.scrape_logger.error(
                f'No schedule data scraped. Please check your input parameters.')
            raise ValueError(
                f'No schedule data scraped. Please check your input parameters.')

        schedule_df = pd.concat(schedule_df_list, axis=0)
        time_taken = time.time() - start_time

        self.scrape_logger.warning(
            '\n-------------------------------------End of Scraping Schedule Info!-------------------------------------')

        # Scraping Statistics
        self.scrape_logger.warning(
            '\n-------------------------------------Scraping Summary-------------------------------------')
        self.scrape_logger.info(
            f'Total schedule page scraped: {pages_to_scrape}')
        self.scrape_logger.info(
            f'Failed Schedule Pages: {len(self.failed_dates)} out of {pages_to_scrape} schedule pages')
        self.scrape_logger.info(
            f'Time elapsed: {time_taken} seconds | {round((time_taken) / 60, 2)} minutes | {round((time_taken) / 3600, 2)} hours')
        self.scrape_logger.info(
            f'Averaged {round((time_taken) / pages_to_scrape, 2)} seconds per schedule page')
        self.scrape_logger.warning(
            '\n------------------------------------------------------------------------------------------------------')

        return schedule_df


class GameDataScraper(AbstractScraper):
    def __init__(self):
        self.base_url = 'https://www.basketball-reference.com/boxscores/shot-chart/{year}{month}{day}0{team}.html'
        self.scrape_logger = Logger(
            name='shots_scraper_logger').scrape_logger
        self.teams = TEAM_ABBS

    def _get_team_abbreviations(self, team_name: str):
        try:
            return TEAM_ABBS[team_name]
        except:
            self.scrape_logger.error(
                f'Failed to get team abbreviation for {team_name}')
            return None

    def _request_soup_for_game(self, year: str, month: str, day: str, team: str):
        try:
            shots = self.rate_limited_request(
                self.base_url.format(year=year, month=month, day=day, team=team))
            soup = BeautifulSoup(shots.content, "html.parser")

            return soup

        except Exception as e:
            raise ValueError(
                f'Invalid input of team={team}: {e}'
            )

    def _request_with_retry(self, year: str, month: str, day: str, team_name: str):

        teams = self._get_team_abbreviations(team_name)

        for team in teams:
            try:
                soup = self._request_soup_for_game(
                    year=year, month=month, day=day, team=team)

                return soup, team

            except ValueError as err:
                self.scrape_logger.error(
                    f'Error occured for {team} on {year}-{month}-{day}: {err}')
            except Exception as err:
                self.scrape_logger.error(
                    f'Error occurred for {team} on {year}-{month}-{day}: {err}')

        self.scrape_logger.error("All team abbreviations exhausted")
        return None

    def _get_shot_area(self, soup: BeautifulSoup):
        try:
            shot_area = soup.find_all("div", class_="shot-area")
            return shot_area
        except:
            self.scrape_logger.error(
                f'Failed to get shot area from BeautifulSoup object')
            return None

    def _get_game_meta(self, soup: BeautifulSoup):
        try:
            game_meta = soup.find_all("div", class_='scorebox_meta')[0].text
            return game_meta
        except:
            self.scrape_logger.error(
                f'Failed to get game meta from BeautifulSoup object')
            return None

    def _get_customdata(self, df: pd.DataFrame) -> list:
        customdata = []
        for row in df.itertuples(index=False):
            customdata.append(tuple(row))
        return customdata

    def _create_df(self, shot_area: BeautifulSoup, game_meta: BeautifulSoup):
        try:
            df = dict(player_name=[], time_left=[], team_name=[], score_status=[],
                      x_shot_pos=[], y_shot_pos=[], quarter=[], shot_status=[], full_text=[])
            for elem in shot_area:
                for content in elem.contents:
                    if isinstance(content, Tag) and not re.search(r'alt="nbahalfcourt"', str(content)):
                        shot_pos = re.findall(
                            r'\d+(?=px)', str(content.attrs.get('style')))
                        tooltip = content.attrs.get('tip')
                        status = content.attrs.get('class')
                        df['x_shot_pos'].append(int(shot_pos[1]))
                        df['y_shot_pos'].append(470 - int(shot_pos[0]))
                        df['quarter'].append(tooltip.split(',')[0])
                        df['time_left'].append(re.findall(
                            r'(?!\s)(\d+:\d+.\d)(?= remaining)', tooltip)[0])
                        df['shot_status'].append(status[-1])
                        df['player_name'].append(re.findall(
                            r"(?=<br>)(.*)((?= missed)|(?= made))", tooltip)[0][0][4:])
                        df['team_name'].append(re.findall(
                            r"(?=ft<br>)(.*)((?= tied)|(?= now trails)|(?= trails)|(?= leads))", tooltip)[0][0][6:].replace('now', ''))
                        df['score_status'].append(re.findall(
                            r"(?=ft<br>).*", tooltip)[0][6:])
                        df['full_text'].append(tooltip)

            df = pd.DataFrame.from_dict(df,).astype({'quarter': 'category',
                                                    'shot_status': 'category', })
            df['datetime'] = dt.datetime.strptime(re.findall(
                r'\d+:\d+ \w+, \w+ \d+, \d+', game_meta)[0], "%I:%M %p, %B %d, %Y")
            # location = re.findall(
            #     r'(?=\d{4})(\w+\s\w+,.+,\s.+)(?=\nLogos)', game_meta)[0][4:].split(',')
            # # arena = location[0].strip()
            # city = location[1].strip()
            # state = location[2].strip()

            # df['arena'] = arena
            # df['city'] = city
            # df['state'] = state

            return df
        except Exception as e:
            self.scrape_logger.error(
                f'Failed to create DataFrame: {e}')
            return None

    def scrape(self, schedule_df: pd.DataFrame):
        """Scrape shots data from each game from basketball-reference.com

        Args:
            schedule_df: Schedule DataFrame. Use the scrape_schedule_data method to get this DataFrame.

        Returns:
            pd.DataFrame: Pandas DataFrame containing shots data.
        """
        df_list = []
        self.failed_games = []
        start_time = time.time()

        self.scrape_logger.warning(
            '\n-------------------------------------Start of Scraping Shot Locations!-------------------------------------\n')

        for row in schedule_df.itertuples():
            team_name = row.Home
            date = row.Index
            year = '{:04d}'.format(date.year)
            month = '{:02d}'.format(date.month)
            day = '{:02d}'.format(date.day)

            self.scrape_logger.info(
                f'Scraping {team_name} on {year}-{month}-{day}: game_id {row.game_id}')

            test_soup, team_abbr = self._request_with_retry(
                year=year, month=month, day=day, team_name=team_name)

            if test_soup is None:
                self.failed_games.append(row.game_id)
                continue

            shot_area = self._get_shot_area(test_soup)

            if shot_area is None:
                self.failed_games.append(row.game_id)
                continue

            game_meta = self._get_game_meta(test_soup)

            if game_meta is None:
                self.failed_games.append(row.game_id)
                continue

            df = self._create_df(shot_area, game_meta)

            if df is None:
                self.failed_games.append(row.game_id)
                continue
            df['game_id'] = row.game_id
            df_list.append(df)

            self.scrape_logger.info(
                f'Successfully processed {row.game_id} shots!\n')

        if len(df_list) == 0:
            self.scrape_logger.error(
                f'No shots data scraped. Please check your input parameters.')
            raise ValueError(
                f'No shots data scraped. Please check your input parameters.')

        shots_df = pd.concat(df_list, axis=0)
        self.scrape_logger.warning(
            '\n-------------------------------------End of Scraping Shot Locations!-------------------------------------')

        time_taken = time.time() - start_time
        games_to_scrape = len(schedule_df)

        # Scraping Statistics
        self.scrape_logger.warning(
            '\n-------------------------------------Scraping Summary-------------------------------------')
        self.scrape_logger.info(
            f'Failed games: {len(self.failed_games)} games out of {games_to_scrape} games')
        self.scrape_logger.info(
            f'Time elapsed: {time_taken} seconds | {round((time_taken) / 60, 2)} minutes | {round((time_taken) / 3600, 2)} hours')
        self.scrape_logger.info(
            f'Averaged {round((time_taken) / games_to_scrape, 2)} seconds per game')
        self.scrape_logger.warning(
            '\n------------------------------------------------------------------------------------------------------')

        return shots_df
