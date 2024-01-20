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
│ └── scraper.py
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


## 🔧 Installation
```
pip install nba-data-scraper
```

## Usage
### Scrape Player Data
```python
from nba_data_scraper import NBAScraper
nba_scraper = NBAScraper()

# Scrapes player data for the letter 'a'
player_data = nba_scraper.scrape_player_data('a')  
```
### Scrape Schedule Data
```python
# Scrapes games played in a specific year and month
schedule_data = nba_scraper.scrape_schedule_data(year='2023', month='january') 

# Scrapes games played in given list of years and months
schedule_data = nba_scraper.scrape_schedule_data(year=['2022','2023'], month=['january','february'])

# Scrapes all games played given a start and end year
schedule_data = nba_scraper.scrape_all_schedule_data(start_year=2020, end_year=2021)
```

### Scrape Game Data
```python
# Scrapes Game Data for games played within a schedule

## First: Scrape for schedule
schedule_data = nba_scraper.scrape_schedule_data(year='2023', month='january')

## Second: use return DataFrame as input to scrape_game_data method
game_data = nba_scraper.scrape_game_data(schedule_df=schedule_data)
```

## License
See the [LICENSE](LICENSE) file for details.