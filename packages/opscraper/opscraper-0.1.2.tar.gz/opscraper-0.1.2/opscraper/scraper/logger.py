import logging
from datetime import datetime

date_today = datetime.today().strftime('%Y-%m-%d')
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Call getLogger with no args to set up the handler
fixture_logger = logging.getLogger()
fixture_logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"/logs/ra-app-oddsportal-fixtures.log", mode='a')
handler.setFormatter(formatter)
fixture_logger.addHandler(handler)


# Call getLogger with no args to set up the handler
odds_logger = logging.getLogger()
odds_logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"/logs/ra-app-oddsportal-odds.log", mode='a')
handler.setFormatter(formatter)
odds_logger.addHandler(handler)
