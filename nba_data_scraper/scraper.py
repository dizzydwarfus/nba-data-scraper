from ._data_scraper import PlayerDataScraper, GameDataScraper


class NBAScraper:
    def __init__(self,):
        self.player_scraper = PlayerDataScraper()
        self.game_scraper = GameDataScraper()
        self._all_letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]

    def scrape_player_data(self, letter):
        return self.player_scraper.scrape(letter)

    def scrape_game_data(self, year, month, day, team):
        return self.game_scraper.scrape(year, month, day, team)
