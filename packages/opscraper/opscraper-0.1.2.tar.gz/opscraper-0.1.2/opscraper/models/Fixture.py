__all__ = ['FixtureModel']

from mongoengine import Document, IntField, StringField, DateTimeField, DynamicDocument

from ..config.localconfig import CONFIG


class FixtureModel(Document):
    id = StringField(primary_key=True)
    game_id = StringField(db_field="gameId", required=True)
    game_oddsportal_id = StringField(db_field="game_oddsportalId", required=True)
    season_id = IntField(db_field="seasonId", required=True)
    competition_oddsportal_id = StringField(db_field="competition_oddsportalId", required=True)
    competition_id = StringField(db_field="competitionId", required=True)
    competition_name = StringField(db_field="competitionName", required=True)
    game_date = DateTimeField(db_field="gameDate", required=True)
    home_team_id = StringField(db_field="homeTeamId", required=True)
    home_team_name = StringField(db_field="homeTeamName", required=True)
    away_team_id = StringField(db_field="awayTeamId", required=True)
    away_team_name = StringField(db_field="awayTeamName", required=True)

    meta = {
        "db_alias": "oddsportal",
        "collection": CONFIG["connections"]["oddsportal"]["fixtures"],
    }


class FixtureMappingModel(DynamicDocument):
    meta = {
        "db_alias": "features",
        "collection": CONFIG["connections"]["features"]["game_features"],
    }