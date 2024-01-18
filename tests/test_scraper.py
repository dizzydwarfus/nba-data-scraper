from nba_data_scraper.scraper import NBAScraper
from nba_data_scraper._constants import TEAM_ABBS, MONTHS

# Testing Libraries
import pytest

# Third-party Libraries
from pandas import DataFrame


@pytest.fixture
def scraper():
    return NBAScraper()


class TestNBAScraperWithoutScraping:
    def test_all_letters(self, scraper):
        assert scraper.all_letters == [
            chr(i) for i in range(ord('a'), ord('z') + 1)]

    def test_teams(self, scraper):
        assert scraper.teams == TEAM_ABBS

    def test_months(self, scraper):
        assert scraper.months == MONTHS

    def test_player_failed_letters_without_scraping(self, scraper):
        with pytest.raises(AttributeError):
            scraper.player_failed_letters

    def test_schedule_failed_dates_without_scraping(self, scraper):
        with pytest.raises(AttributeError):
            scraper.schedule_failed_dates

    def test_games_failed_game_ids_without_scraping(self, scraper):
        with pytest.raises(AttributeError):
            scraper.games_failed_game_ids

    def test_schedule_df_without_scraping(self, scraper):
        with pytest.raises(AttributeError):
            scraper.schedule_df

    def test_shots_from_games_without_scraping(self, scraper):
        with pytest.raises(AttributeError):
            scraper.shots_from_games


class TestPlayerScraperInputs:
    @pytest.mark.parametrize('input', [
        ('a')
    ])
    def test_player_data_scraper_success_string_input(self, scraper, input):
        result = scraper.scrape_player_data(input)
        assert isinstance(result, DataFrame) and len(
            result) > 0

    @pytest.mark.parametrize('input,expected', [
        (['a', 'afwfea'], ['afwfea'])
    ])
    def test_player_data_scraper_success_list_input(self, scraper, input, expected):
        result = scraper.scrape_player_data(input)
        assert isinstance(result, DataFrame) and len(
            result) > 0 and scraper.player_failed_letters == expected

    @pytest.mark.parametrize('input', [
        (['21213', 'szz0921']),
        (''),
        ('21312')
    ])
    def test_player_data_scraper_value_error_input(self, scraper, input):
        with pytest.raises(ValueError):
            scraper.scrape_player_data(input)

    @pytest.mark.parametrize('input', [
        ([]),
        (),
        (123)
    ])
    def test_player_data_scraper_type_error_input(self, scraper, input):
        with pytest.raises(TypeError):
            scraper.scrape_player_data(input)


class TestScheduleScraperInputs:
    @pytest.mark.parametrize('year,month,failed', [
        ('2018', 'november', []),
        (['2018', '2019'], ['november', 'december'], []),
        (['2018', '2019'], 'november', []),
        ('2018', ['november', 'december'], []),
        (['2018', 2018], 'november', []),
        (['2018', '213211'], 'november', ['213211-november']),
    ])
    def test_schedule_data_scraper_success_input(self, scraper, year, month, failed):
        result = scraper.scrape_schedule_data(
            year=year, month=month)
        assert isinstance(result, DataFrame) and len(
            result) > 0 and scraper.schedule_failed_dates == failed

    @pytest.mark.parametrize('year,month, failed', [
        ('2131231', 'november', ['2131231-november']),
        (['2131', 1232], ['wfpawejf'], ['2131-wfpawejf', '1232-wfpawejf']),
        ([], [], []),
        ('', '', ['-']),
    ])
    def test_schedule_data_scraper_value_error_input(self, scraper, year, month, failed):
        with pytest.raises(ValueError):
            scraper.scrape_schedule_data(year=year, month=month)
        assert scraper.schedule_failed_dates == failed

    @pytest.mark.parametrize('year,month', [
        (None, None),
        (123, 123),
    ])
    def test_schedule_data_scraper_type_error_input(self, scraper, year, month):
        with pytest.raises(TypeError):
            scraper.scrape_schedule_data(year=year, month=month)


@pytest.fixture(scope='session')
def game_scraper():
    s = NBAScraper()
    s.scrape_schedule_data(year=['2018'], month='november')
    return s


@pytest.fixture(scope='session')
def schedule_df(game_scraper):
    return game_scraper.schedule_df.iloc[:1]


class TestGameScraperInputs:
    @pytest.mark.parametrize('input', [
        (schedule_df)
    ])
    def test_game_data_scraper_success_df_input(self, scraper, input):
        result = scraper.scrape_game_data(
            schedule_df=input)

        is_dataframe = isinstance(result, DataFrame)
        len_result = len(result) > 0

        assert is_dataframe and len_result and scraper.games_failed_game_ids == []

    @pytest.mark.parametrize('input', [
        (DataFrame()),
        (None)
    ])
    def test_game_data_scraper_invalid_df_input(self, scraper, input):
        with pytest.raises(ValueError):
            scraper.scrape_game_data(
                schedule_df=input)

    @pytest.mark.parametrize('input,failed', [
        (DataFrame({'a': [1, 2], 'b': [3, 4]}), []),
        ('a', []),
        ([], []),
        (123, [])
    ])
    def test_game_data_scraper_invalid_int_input(self, scraper, input, failed):
        with pytest.raises(AttributeError):
            scraper.scrape_game_data(schedule_df=input)

        assert scraper.games_failed_game_ids == failed
