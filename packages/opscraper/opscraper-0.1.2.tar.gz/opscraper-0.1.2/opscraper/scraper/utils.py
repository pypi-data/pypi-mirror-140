import json
import re
import time
from datetime import timedelta

import pandas as pd
import requests
from lxml import html
from mongoengine import Q

from opscraper.config.localconfig import API_BASE_URL
from opscraper.models.Competition import CompetitionModel
from opscraper.models.Fixture import FixtureMappingModel, FixtureModel
from opscraper.models.Teams import TeamsMappingModel

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,pl;q=0.8",
    "referer": "https://www.oddsportal.com/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 "
                  "Safari/537.36 "
}


def get_response(url: str) -> str:
    return requests.get(url, headers=headers).text


def get_fixture_result_url(page_number: int, competition_id: str, is_past: bool) -> str:
    time_now_ms = int(round(time.time() * 1000))
    if is_past:
        fixture_page_url = f"{API_BASE_URL}/ajax-sport-country-tournament-archive/1/" \
                           f"{competition_id}/X0/1/1/{page_number}/?_={time_now_ms}"
    else:
        fixture_page_url = f"{API_BASE_URL}/ajax-sport-country-tournament/1/" \
                           f"{competition_id}/X0/1/?_={time_now_ms}"
    return fixture_page_url


def get_last_page_fixture(result_page_request: str) -> int:
    result_page_response = get_response(result_page_request)
    json_response = re.findall(r",\s({.*})", result_page_response)
    results_data = json.loads(json_response[0])
    results_html = results_data.get("d").get("html")
    html_doc = html.fromstring(results_html)
    page_links = html_doc.xpath("//div[@id='pagination']//a")
    last_page = 1
    if page_links:
        last_page = int(page_links[-1].get("x-page"))

    return last_page


def decode_uid(xhash):
    decoded_uid = ''
    for i in xhash.split('%')[1:]:
        decoded_uid += chr(int(i, 16))
    return decoded_uid


def competition_metadata(competition_id: str, season_id: int, fixture_logger):
    competition = CompetitionModel.objects(competition_id=competition_id,
                                           season_id=season_id)
    if not competition:
        fixture_logger.error("Competition not found")

    return competition


def get_available_odds(current_odd, odds_history, odd_type):
    odds_history = [{f"odds{odd_type}": float(single_snapshot[0]),
                     "timestamp": single_snapshot[2]} for
                    single_snapshot in odds_history]
    odds_history.append(current_odd)
    return odds_history


def get_all_odds(one_odds, two_odds, x_odds=None, is_triple_market_odds=True):
    x_ts = []

    one_df = pd.DataFrame(one_odds)
    one_df.sort_values('timestamp', inplace=True)
    two_df = pd.DataFrame(two_odds)
    two_df.sort_values('timestamp', inplace=True)

    if is_triple_market_odds:
        x_ts = [ts['timestamp'] for ts in x_odds]
        x_df = pd.DataFrame(x_odds)
        x_df.sort_values('timestamp', inplace=True)

    one_ts = [ts['timestamp'] for ts in one_odds]
    two_ts = [ts['timestamp'] for ts in two_odds]

    all_timestamps = one_ts + x_ts + two_ts

    ts_df = pd.DataFrame(data={"timestamp": (pd.unique(all_timestamps))})
    ts_df.sort_values('timestamp', inplace=True)

    ts_df = pd.merge_asof(ts_df, one_df, on="timestamp", direction='nearest')
    all_odds_df = pd.merge_asof(ts_df, two_df, on="timestamp", direction='nearest')
    if is_triple_market_odds:
        all_odds_df = pd.merge_asof(all_odds_df, x_df, on="timestamp", direction='nearest')
    return all_odds_df


def map_single_game(game: FixtureModel, fixture_logger):
    teams = TeamsMappingModel.objects()
    home_team_document = teams.filter(Q(oddsportalName=game.home_team_name))
    away_team_document = teams.filter(Q(oddsportalName=game.away_team_name))
    if home_team_document and away_team_document:
        game.home_team_id = home_team_document[0].id
        game.away_team_id = away_team_document[0].id
    elif not home_team_document:
        fixture_logger.error(f"Could not map home team {game.away_team_name} for game ID : {game.game_oddsportal_id}")
        return False
    elif not away_team_document:
        fixture_logger.error(f"Could not map away team {game.away_team_name} for game ID : {game.game_oddsportal_id}")
        return False

    max_game_date = game.game_date + timedelta(days=7)
    min_game_date = game.game_date - timedelta(days=1)
    mapped_game = FixtureMappingModel.objects(homeTeamId=game.home_team_id,
                                              awayTeamId=game.away_team_id,
                                              competitionId=game.competition_id,
                                              seasonId=game.season_id,
                                              gameDate__gte=min_game_date,
                                              gameDate__lte=max_game_date)
    if mapped_game:
        game.game_id = mapped_game[0].gameId
    else:
        fixture_logger.error(f"Could not find a mapped game for game ID : {game.game_oddsportal_id}")
        return False

    game.save()
    fixture_logger.info(f"Game opscraper ID : {game.game_oddsportal_id} matches RA Game ID : {game.game_id}")
    return game
