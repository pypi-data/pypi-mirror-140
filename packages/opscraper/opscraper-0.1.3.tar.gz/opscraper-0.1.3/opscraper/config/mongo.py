__all__ = ['db_connect', 'mongo_init', 'mongo_init_prod_backup']


from typing import Optional

import mongoengine

from .localconfig import CONFIG, DB_HOSTS


def db_connect(db_host: str, db_name: str, db_alias: Optional[str] = None):
    """Connect to the apprpriate mongo database

    The function will form the appropriate uri-string and then pass it to `mongoengine.resgister_connection()`

    Parameters
    ----------
    db_host : str
        Host name as defined in `DB_HOSTS`
    db_name: str
        Name of the database to connect to
    db_alias: str, optional
        alias of the database we are connecting to. If not provided, we will use `db_name`

    """
    # check that the host name provided is valid
    if db_host not in DB_HOSTS:
        raise ValueError(
            "db-host provided {db_host} should be one of {hosts}:".format(
                db_host=db_host, hosts=DB_HOSTS
            )
        )

    # decide on the alias to apply
    db_alias = db_name if not db_name else db_alias

    # read config for the appropriate database
    db_config = CONFIG["databases"][db_host]

    # form the mongo-url i.e check if we need the port
    db_url = (
        db_config["url"]
        if not db_config["port"]
        else db_config["url"] + ":" + str(db_config["port"])
    )

    db_uri = "{base_url}{user}:{password}@{url}/{db}".format(
        base_url=db_config["mongo_base"],
        user=db_config["user"],
        password=db_config["password"],
        url=db_url,
        db=db_name,
    )
    # add optional argument
    optional_uri = []
    if db_config["majority"]:
        optional_uri.append("w={majority}".format(majority="majority"))
    if db_config["retry_writes"]:
        optional_uri.append(
            "retryWrites={majority}".format(
                majority=str(db_config["retry_writes"]).lower()
            )
        )
    if db_config["authSource"]:
        optional_uri.append(
            "authSource={auth_db}".format(auth_db=db_config["authSource"])
        )

    if optional_uri:
        db_uri += "?" + "&".join(optional_uri)

    mongoengine.register_connection(host=db_uri, alias=db_alias, name=db_name)

# Cell


def mongo_init(db_host: str):
    """
    Register all the required mongo connections

    Parameters
    ----------
    db_host : str
        Host name as defined in `DB_HOSTS`

    """
    # check that the host name provided is valid
    if db_host not in DB_HOSTS:
        raise ValueError(
            "db-host provided {db_host} should be one of {hosts}:".format(
                db_host=db_host, hosts=DB_HOSTS
            )
        )

    # opscraper db
    db_connect(
        db_host=db_host,
        db_name=CONFIG["connections"]["oddsportal"]["db"],
        db_alias="oddsportal",
    )

    # mapping db
    db_connect(
        db_host=db_host,
        db_name=CONFIG["connections"]["mapping"]["db"],
        db_alias="mapping",
    )

    # features db
    db_connect(
        db_host=db_host,
        db_name=CONFIG["connections"]["features"]["db"],
        db_alias="features",
    )


def mongo_init_prod_backup(db_host: str):
    """
    Register all the required mongo connections

    Parameters
    ----------
    db_host : str
        Host name as defined in `DB_HOSTS`

    """

    # oddsportal db
    db_connect(
        db_host=db_host,
        db_name=CONFIG["connections"]["oddsportal_prod_backup"]["db"],
        db_alias="oddsportal_prod_backup",
    )
