from mongoengine import DynamicDocument

from opscraper.config.localconfig import CONFIG


class TeamsMappingModel(DynamicDocument):
    meta = {
        "db_alias": "mapping",
        "collection": CONFIG["connections"]["mapping"]["teams"],
    }