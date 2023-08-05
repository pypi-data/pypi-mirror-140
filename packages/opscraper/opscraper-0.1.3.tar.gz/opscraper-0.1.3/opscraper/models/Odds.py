__all__ = ['OddsModel', 'OddsProdModel', 'OddsLiveModel']

from mongoengine import Document, IntField, StringField, DateTimeField, FloatField

from ..config.localconfig import CONFIG


class OddsModel(Document):
    id = StringField(primary_key=True)
    game_id = StringField(db_field="gameId", required=True)
    season_id = IntField(db_field="seasonId", required=True)
    competition_id = StringField(db_field="competitionId", required=True)
    game_date = DateTimeField(db_field="gameDate", required=True)
    home_team_id = StringField(db_field="homeTeamId", required=True)
    away_team_id = StringField(db_field="awayTeamId", required=True)
    bookmaker_name = StringField(db_field="bookmakerName", required=True)
    bookmaker_id = IntField(db_field="bookmakerId", required=True)
    time_received = DateTimeField(db_field="timeReceived", required=True)
    source = StringField(db_field="source", required=True)
    market_type = StringField(db_field="marketType", required=True)
    odds1 = FloatField(db_field="odds1", required=True)
    odds2 = FloatField(db_field="odds2", required=True)
    oddsX = FloatField(db_field="oddsX", required=False)
    line_type = FloatField(db_field="lineId", required=False)

    meta = {
        "db_alias": "oddsportal",
        "collection": CONFIG["connections"]["oddsportal"]["odds"],
    }


class OddsProdModel(Document):
    id = StringField(primary_key=True)
    game_id = StringField(db_field="gameId", required=True)
    season_id = IntField(db_field="seasonId", required=True)
    competition_id = StringField(db_field="competitionId", required=True)
    game_date = DateTimeField(db_field="gameDate", required=True)
    home_team_id = StringField(db_field="homeTeamId", required=True)
    away_team_id = StringField(db_field="awayTeamId", required=True)
    bookmaker_name = StringField(db_field="bookmakerName", required=True)
    bookmaker_id = IntField(db_field="bookmakerId", required=True)
    time_received = DateTimeField(db_field="timeReceived", required=True)
    source = StringField(db_field="source", required=True)
    market_type = StringField(db_field="marketType", required=True)
    odds1 = FloatField(db_field="odds1", required=True)
    odds2 = FloatField(db_field="odds2", required=True)
    oddsX = FloatField(db_field="oddsX", required=False)
    line_type = FloatField(db_field="lineId", required=False)

    meta = {
        "db_alias": "features",
        "collection": CONFIG["connections"]["features"]["odds"],
    }


class OddsLiveModel(Document):
    id = StringField(primary_key=True)
    game_id = StringField(db_field="gameId", required=True)
    season_id = IntField(db_field="seasonId", required=True)
    competition_id = StringField(db_field="competitionId", required=True)
    game_date = DateTimeField(db_field="gameDate", required=True)
    home_team_id = StringField(db_field="homeTeamId", required=True)
    away_team_id = StringField(db_field="awayTeamId", required=True)
    bookmaker_name = StringField(db_field="bookmakerName", required=True)
    bookmaker_id = IntField(db_field="bookmakerId", required=True)
    time_received = DateTimeField(db_field="timeReceived", required=True)
    source = StringField(db_field="source", required=True)
    market_type = StringField(db_field="marketType", required=True)
    odds1 = FloatField(db_field="odds1", required=True)
    odds2 = FloatField(db_field="odds2", required=True)
    oddsX = FloatField(db_field="oddsX", required=False)
    line_type = FloatField(db_field="lineId", required=False)

    meta = {
        "db_alias": "oddsportal_prod_backup",
        "collection": CONFIG["connections"]["oddsportal_prod_backup"]["liveodds"],
    }
