import json
import logging
import re
from datetime import datetime

from lxml import html

from opscraper.config.localconfig import BASE_URL
from opscraper.models.Fixture import FixtureModel
from opscraper.scraper.logger import fixture_logger
from opscraper.scraper.utils import get_fixture_result_url, get_last_page_fixture, get_response, \
    competition_metadata, map_single_game


class Fixture:
    def __init__(self, competition_id: str, season_id: int, is_past: bool):
        self.is_past = is_past
        self.competition = competition_metadata(competition_id=competition_id,
                                                season_id=season_id,
                                                fixture_logger=fixture_logger)[0]
        if is_past:
            self.parse_historical_fixtures()
        else:
            self.parse_future_fixtures()

    def parse_future_fixtures(self):
        competition_url = self.competition.competition_url
        url = BASE_URL + competition_url
        next_fixtures_response = get_response(url)
        fixture_logger.info(f"Extracting future games from {self.competition.competition_name}")
        self.extract_games_from_page(next_fixtures_response)

    def parse_historical_fixtures(self):
        competition_id = self.competition.competition_oddsportal_id
        result_page_request = get_fixture_result_url(page_number=1,
                                                     competition_id=competition_id,
                                                     is_past=self.is_past)

        last_page = get_last_page_fixture(result_page_request)
        for page_number in range(1, last_page + 1):
            fixture_logger.info(f"Extracting games from page number {page_number}")
            self.get_historical_per_page(page_number=page_number)

    def get_historical_per_page(self, page_number):
        competition_id = self.competition.competition_oddsportal_id
        result_page_request = get_fixture_result_url(page_number=page_number,
                                                     competition_id=competition_id,
                                                     is_past=self.is_past)
        result_page_response = get_response(result_page_request)
        json_response = re.findall(r",\s({.*})", result_page_response)
        results_data = json.loads(json_response[0])
        games_html = results_data.get("d").get("html")
        self.extract_games_from_page(games_html)

    def extract_games_from_page(self, games_html):
        competition_id = self.competition.competition_oddsportal_id
        html_doc = html.fromstring(games_html)
        games = html_doc.xpath("//table[@id='tournamentTable']//tr[td[@class='name table-participant']]")
        fixture_logger.info(f"{len(games)} games found")
        for single_game in games:
            oddsportal_game_id = single_game.get("xeid")
            timestamp_raw = single_game.xpath("td[contains(@class,'table-time')]")[0].get("class")
            timestamp = re.search(r"[0-9]+", timestamp_raw)[0]
            game_date = datetime.utcfromtimestamp(int(timestamp))
            ht_at_raw = single_game.xpath("td[@class='name table-participant']/a//text()")
            ht_at = "".join(ht_at_raw).replace(u'\xa0', '').split(" - ")
            home_team_name = ht_at[0].strip()
            away_team_name = ht_at[1].strip()
            logging.info(f"gameId : {oddsportal_game_id},"
                         f" competitionId : {self.competition.competition_name},"
                         f" Season : {self.competition.season_id}")
            game = FixtureModel(id=f"{oddsportal_game_id}_{competition_id}",
                                game_oddsportal_id=oddsportal_game_id,
                                competition_oddsportal_id=competition_id,
                                competition_id=self.competition.competition_ra_id,
                                competition_name=self.competition.competition_name,
                                season_id=self.competition.season_id,
                                game_date=game_date,
                                home_team_name=home_team_name,
                                away_team_name=away_team_name
                                )
            map_single_game(game, fixture_logger)
