# NBA Data Scraper

## Introduction
NBA Data Scraper is a Python library designed to scrape game shots data from a specific basketball-related website ([Basketball Reference](https://www.sports-reference.com/bot-traffic.html])). It is structured to handle requests efficiently and respectfully using rate limiting to avoid overloading the server ([bot traffic](https://www.sports-reference.com/bot-traffic.html)). On that note, all use of data acquired should respect the website's [terms of use](https://www.sports-reference.com/data_use.html).

## 📂 Structure
```
nba-data-scraper/
│
├── nba-data-scraper/
│ ├── init.py
│ ├── utils/
│ │ ├── init.py
│ │ └── _logger.py
│ ├── _abstract.py
│ ├── _data_scraper.py
│ └── _scraper.py
│
├── tests/
│ ├── init.py
│ └── ...
│
├── docs/
│ └── ...
│
├── examples/
│ └── ...
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```


## 🔧 Installation (not available yet)
(Instructions on how to install the library, e.g., using pip or by cloning the repo)
```
pip install nba-data-scraper
```

## Usage
### Scrape Player Data
```python
from nba-data-scraper._scraper import NBAScraper

nba_scraper = NBAScraper()
player_data = nba_scraper.scrape_player_data('a')  # Scrapes player data for the letter 'a'
```
### Scrape Game Data
```python
game_data = nba_scraper.scrape_game_data('2024', '01', '15', 'LAL')  # Scrapes game data for a specific date and team
```

## Work in Progress
- Further documentation in the docs/ folder.
- Additional examples in the examples/ folder.
- Comprehensive tests in the tests/ folder.

## License
