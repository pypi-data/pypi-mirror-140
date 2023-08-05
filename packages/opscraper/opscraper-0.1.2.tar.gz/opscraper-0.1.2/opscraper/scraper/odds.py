import json

import re
import time
from datetime import datetime

from opscraper.config.localconfig import BASE_URL, API_BASE_URL
from opscraper.models.Fixture import FixtureModel
from opscraper.scraper.logger import odds_logger
from opscraper.models.Odds import OddsModel, OddsProdModel, OddsLiveModel
from opscraper.scraper.utils import decode_uid, get_response, get_available_odds, get_all_odds

bookmakers = {
    "PinnacleSports": "18",
    "sbobet": "75",
    "MarathonBet": "381",
    "bet365": "16"
}

markets = {
    "1x2": "1-2",
    "asian": "5-2",
    "total": "2-2"
}


class Odds:
    def __init__(self, game_id: str, live=False):
        self.live = live
        self.game_oddsportal_id = game_id
        self.base_document = None
        self.hash_uid = self.get_hash_uid()
        self.game = FixtureModel.objects(game_oddsportal_id=game_id)[0]
        self.init_mongo_document()
        for market in markets.keys():
            self.get_odds(market)

    def get_hash_uid(self):
        game_url = BASE_URL + f"/a/b/c/d-{self.game_oddsportal_id}/"
        html = get_response(game_url)
        hash_uid = decode_uid(re.findall(r'xhash":"([^"]+)"', html)[0])
        odds_logger.info({"game_id": {self.game_oddsportal_id}, "hashkey": {hash_uid}, "message": "decode hash key", "function": "get_hash_uid"})
        return hash_uid

    def get_odds(self, market_type: str):
        code_market = markets[market_type]
        odds_data = self.get_odds_json(market_code=code_market)

        if odds_data["d"]["oddsdata"]["back"]:
            odds_code = odds_data["d"]["oddsdata"]["back"].keys()
            for single_line in odds_code:
                current_odds = odds_data["d"]["oddsdata"]["back"][single_line]
                historical_odds = odds_data["d"]["history"]["back"]
                if market_type == "1x2":
                    self.get_one_x_two(current_odds, historical_odds, market_type)
                else:
                    self.get_double_market_odds(current_odds, historical_odds, market_type)

    def get_one_x_two(self, odds, historical_odds, market_type):
        outcome_uid = odds["outcomeId"]
        current_odds = odds["odds"]
        current_changing_time = odds["changeTime"]

        if isinstance(outcome_uid, list):
            odd_one_uid = outcome_uid[0]
            odd_x_uid = outcome_uid[1]
            odd_two_uid = outcome_uid[2]
            for bookmaker_name, bookmaker_id in bookmakers.items():
                if bookmaker_id in current_odds:
                    current_one_odd = {"odds1": float(current_odds[bookmaker_id][0]),
                                       "timestamp": current_changing_time[bookmaker_id][0]}
                    current_x_odd = {"oddsX": float(current_odds[bookmaker_id][1]),
                                     "timestamp": current_changing_time[bookmaker_id][1]}
                    current_two_odd = {"odds2": float(current_odds[bookmaker_id][2]),
                                       "timestamp": current_changing_time[bookmaker_id][2]}

                    one_odds_history = historical_odds[odd_one_uid][bookmaker_id]
                    x_odds_history = historical_odds[odd_x_uid][bookmaker_id]
                    two_odds_history = historical_odds[odd_two_uid][bookmaker_id]

                    one_odds = get_available_odds(current_one_odd, one_odds_history, "1")
                    x_odds = get_available_odds(current_x_odd, x_odds_history, "X")
                    two_odds = get_available_odds(current_two_odd, two_odds_history, "2")
                    one_x_two_df = get_all_odds(one_odds=one_odds, x_odds=x_odds, two_odds=two_odds)
                    if self.live:
                        self.insert_1x2_live_df(one_x_two_df, bookmaker_id, bookmaker_name, market_type)
                    else:
                        self.insert_1x2_df(one_x_two_df, bookmaker_id, bookmaker_name, market_type)
        else:
            odd_one_uid = outcome_uid["0"]
            odd_x_uid = outcome_uid["1"]
            odd_two_uid = outcome_uid["2"]
            for bookmaker_name, bookmaker_id in bookmakers.items():
                if bookmaker_id in current_odds:
                    current_one_odd = {"odds1": float(current_odds[bookmaker_id]["0"]),
                                       "timestamp": current_changing_time[bookmaker_id]["0"]}
                    current_x_odd = {"oddsX": float(current_odds[bookmaker_id]["1"]),
                                     "timestamp": current_changing_time[bookmaker_id]["1"]}
                    current_two_odd = {"odds2": float(current_odds[bookmaker_id]["2"]),
                                       "timestamp": current_changing_time[bookmaker_id]["2"]}

                    one_odds_history = historical_odds[odd_one_uid][bookmaker_id]
                    x_odds_history = historical_odds[odd_x_uid][bookmaker_id]
                    two_odds_history = historical_odds[odd_two_uid][bookmaker_id]

                    one_odds = get_available_odds(current_one_odd, one_odds_history, "1")
                    x_odds = get_available_odds(current_x_odd, x_odds_history, "X")
                    two_odds = get_available_odds(current_two_odd, two_odds_history, "2")
                    one_x_two_df = get_all_odds(one_odds=one_odds, x_odds=x_odds, two_odds=two_odds)
                    if self.live:
                        self.insert_1x2_live_df(one_x_two_df, bookmaker_id, bookmaker_name, market_type)
                    else:
                        self.insert_1x2_df(one_x_two_df, bookmaker_id, bookmaker_name, market_type)

    def insert_1x2_df(self, one_x_two_odds_df, bookmaker_id, bookmaker_name, market):
        for index, row in one_x_two_odds_df.iterrows():
            timestamp = int(row["timestamp"])
            document_id = f"{self.game.game_id}_{bookmaker_id}_{market}_{timestamp}"
            odd_document = OddsModel(**self.base_document)
            odd_document.id = document_id
            odd_document.odds1 = float(row["odds1"])
            odd_document.oddsX = float(row["oddsX"])
            odd_document.odds2 = float(row["odds2"])
            odd_document.bookmaker_id = bookmaker_id
            odd_document.bookmaker_name = bookmaker_name
            odd_document.market_type = market
            time_received = datetime.utcfromtimestamp(int(timestamp))
            odd_document.time_received = time_received
            odd_document.save()
            prod_odd_document = OddsProdModel(**self.base_document)
            prod_odd_document.id = document_id
            prod_odd_document.odds1 = float(row["odds1"])
            prod_odd_document.oddsX = float(row["oddsX"])
            prod_odd_document.odds2 = float(row["odds2"])
            prod_odd_document.bookmaker_id = bookmaker_id
            prod_odd_document.bookmaker_name = bookmaker_name
            prod_odd_document.market_type = market
            prod_odd_document.time_received = time_received
            prod_odd_document.save()

    def insert_1x2_live_df(self, one_x_two_odds_df, bookmaker_id, bookmaker_name, market):
        for index, row in one_x_two_odds_df.iterrows():
            timestamp = int(row["timestamp"])
            document_id = f"{self.game.game_id}_{bookmaker_id}_{market}_{timestamp}"
            odd_document = OddsLiveModel(**self.base_document)
            odd_document.id = document_id
            odd_document.odds1 = float(row["odds1"])
            odd_document.oddsX = float(row["oddsX"])
            odd_document.odds2 = float(row["odds2"])
            odd_document.bookmaker_id = bookmaker_id
            odd_document.bookmaker_name = bookmaker_name
            odd_document.market_type = market
            time_received = datetime.utcfromtimestamp(int(timestamp))
            odd_document.time_received = time_received
            odd_document.save()

    def get_double_market_odds(self, odds, historical_odds, market_type):
        outcome_uid = odds["outcomeId"]
        current_odds = odds["odds"]
        current_changing_time = odds["changeTime"]
        line_id = odds["handicapValue"]
        if isinstance(outcome_uid, list):
            odd_one_uid = outcome_uid[0]
            odd_two_uid = outcome_uid[1]
            for bookmaker_name, bookmaker_id in bookmakers.items():
                if bookmaker_id in current_odds:
                    current_one_odd = {"odds1": float(current_odds[bookmaker_id][0]),
                                       "timestamp": current_changing_time[bookmaker_id][0]}
                    current_two_odd = {"odds2": float(current_odds[bookmaker_id][1]),
                                       "timestamp": current_changing_time[bookmaker_id][1]}

                    one_odds_history = historical_odds[odd_one_uid][bookmaker_id]
                    two_odds_history = historical_odds[odd_two_uid][bookmaker_id]

                    one_odds = get_available_odds(current_one_odd, one_odds_history, "1")
                    two_odds = get_available_odds(current_two_odd, two_odds_history, "2")
                    double_odds_df = get_all_odds(one_odds=one_odds, two_odds=two_odds,
                                                  is_triple_market_odds=False)
                    if self.live:
                        self.insert_double_odds_live_df(double_odds_df, bookmaker_id, bookmaker_name,
                                                        line_id, market_type)
                    else:
                        self.insert_double_odds_df(double_odds_df, bookmaker_id, bookmaker_name,
                                                   line_id, market_type)
        else:
            odd_one_uid = outcome_uid["0"]
            odd_two_uid = outcome_uid["1"]
            for bookmaker_name, bookmaker_id in bookmakers.items():
                if bookmaker_id in current_odds:
                    current_one_odd = {"odds1": float(current_odds[bookmaker_id]["0"]),
                                       "timestamp": current_changing_time[bookmaker_id]["0"]}
                    current_two_odd = {"odds2": float(current_odds[bookmaker_id]["1"]),
                                       "timestamp": current_changing_time[bookmaker_id]["1"]}

                    one_odds_history = historical_odds[odd_one_uid][bookmaker_id]
                    two_odds_history = historical_odds[odd_two_uid][bookmaker_id]

                    one_odds = get_available_odds(current_one_odd, one_odds_history, "1")
                    two_odds = get_available_odds(current_two_odd, two_odds_history, "2")
                    double_odds_df = get_all_odds(one_odds=one_odds, two_odds=two_odds,
                                                  is_triple_market_odds=False)
                    if self.live:
                        self.insert_double_odds_live_df(double_odds_df, bookmaker_id, bookmaker_name,
                                                        line_id, market_type)
                    else:
                        self.insert_double_odds_df(double_odds_df, bookmaker_id, bookmaker_name,
                                                   line_id, market_type)

    def insert_double_odds_df(self, one_x_two_odds_df, bookmaker_id, bookmaker_name, line_id, market):
        for index, row in one_x_two_odds_df.iterrows():
            timestamp = int(row["timestamp"])
            document_id = f"{self.game.game_id}_{bookmaker_id}_{market}_{timestamp}"
            odd_document = OddsModel(**self.base_document)
            odd_document.id = document_id
            odd_document.odds1 = float(row["odds1"])
            odd_document.odds2 = float(row["odds2"])
            odd_document.bookmaker_id = bookmaker_id
            odd_document.bookmaker_name = bookmaker_name
            odd_document.market_type = market
            odd_document.line_type = float(line_id)
            time_received = datetime.utcfromtimestamp(int(timestamp))
            odd_document.time_received = time_received
            try:
                odd_document.save()
                odds_logger.info({"gameId": {self.game.game_id}, "database": "oddsportal", "bookmaker": {bookmaker_name}, "message": "successfully inserted", "function": "insert_double_odds_df"})
            except:
                odds_logger.error({"gameId": {self.game.game_id}, "database": "oddsportal", "bookmaker": {bookmaker_name}, "message": "failed to insert", "function": "insert_double_odds_df"})

            prod_odd_document = OddsProdModel(**self.base_document)
            prod_odd_document.id = document_id
            prod_odd_document.odds1 = float(row["odds1"])
            prod_odd_document.odds2 = float(row["odds2"])
            prod_odd_document.bookmaker_id = bookmaker_id
            prod_odd_document.bookmaker_name = bookmaker_name
            prod_odd_document.market_type = market
            prod_odd_document.line_type = float(line_id)
            prod_odd_document.time_received = time_received
            try:
                prod_odd_document.save()
                odds_logger.info({"gameId": {self.game.game_id}, "database": "prod", "bookmaker": {bookmaker_name}, "message": "successfully inserted", "function": "insert_double_odds_df"})
            except:
                odds_logger.error({"gameId": {self.game.game_id}, "database": "prod", "bookmaker": {bookmaker_name}, "message": "failed to insert", "function": "insert_double_odds_df"})

            

    def insert_double_odds_live_df(self, one_x_two_odds_df, bookmaker_id, bookmaker_name, line_id, market):
        for index, row in one_x_two_odds_df.iterrows():
            timestamp = int(row["timestamp"])
            document_id = f"{self.game.game_id}_{bookmaker_id}_{market}_{timestamp}"
            odd_document = OddsLiveModel(**self.base_document)
            odd_document.id = document_id
            odd_document.odds1 = float(row["odds1"])
            odd_document.odds2 = float(row["odds2"])
            odd_document.bookmaker_id = bookmaker_id
            odd_document.bookmaker_name = bookmaker_name
            odd_document.market_type = market
            odd_document.line_type = float(line_id)
            time_received = datetime.utcfromtimestamp(int(timestamp))
            odd_document.time_received = time_received
            odd_document.save()

    def init_mongo_document(self):
        base_document = {"game_id": self.game.game_id,
                         "season_id": self.game.season_id,
                         "competition_id": self.game.competition_id,
                         "game_date": self.game.game_date,
                         "home_team_id": self.game.home_team_id,
                         "away_team_id": self.game.away_team_id,
                         "source": "oddsportal"}
        self.base_document = base_document

    def get_odds_json(self, market_code: str):
        prefix_url = "/feed/match/"
        if self.live:
            prefix_url = "/feed/live/"
        while True:
            time_now_ms = int(round(time.time() * 1000))
            game_api_url = \
                API_BASE_URL + prefix_url + f"1-1-{self.game_oddsportal_id}-{market_code}-{self.hash_uid}.dat?_={time_now_ms}"
            odds_data = json.loads(re.findall(r"\.dat',\s({.*})", get_response(game_api_url))[0])
            if "E" not in odds_data["d"]:
                odds_logger.info({"game_id": {self.game_oddsportal_id}, "hashkey":{self.hash_uid}, "message": "Successfully decode json odds", "function": "get_odds_json"})
                return odds_data
            self.hash_uid = self.get_hash_uid()
            odds_logger.info({"game_id": {self.game_oddsportal_id}, "hashkey":{self.hash_uid}, "message": "Failed decode json odds", "function": "get_odds_json"})
            time.sleep(2)
