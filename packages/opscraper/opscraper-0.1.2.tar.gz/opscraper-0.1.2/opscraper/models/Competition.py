__all__ = ['CompetitionModel']

from mongoengine import Document, IntField, StringField

from ..config.localconfig import CONFIG


class CompetitionModel(Document):
    id = StringField(primary_key=True)
    competition_oddsportal_id = StringField(db_field="competition_oddsportalId", required=True)
    season_id = IntField(db_field="seasonId", required=True)
    competition_ra_id = StringField(db_field="ra_competitionId", required=True)
    competition_id = StringField(db_field="competitionId", required=True)
    competition_name = StringField(db_field="competitionName", required=True)
    competition_url = StringField(db_field="competitionUrl", required=True)

    meta = {
        "db_alias": "oddsportal",
        "collection": CONFIG["connections"]["oddsportal"]["competitions"],
    }
