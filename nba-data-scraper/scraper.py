from ._data_scraper import PlayerDataScraper, GameDataScraper


class NBAScraper:
    def __init__(self, player_url, game_url):
        self.player_scraper = PlayerDataScraper(player_url)
        self.game_scraper = GameDataScraper(game_url)
        self._all_letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]

    def scrape_player_data(self, letter):
        return self.player_scraper.scrape(letter)

    def scrape_game_data(self, year, month, day, team):
        return self.game_scraper.scrape(year, month, day, team)
