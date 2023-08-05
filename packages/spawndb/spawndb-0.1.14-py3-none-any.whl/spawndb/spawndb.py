from typing import *

from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine, text, MetaData


_engine: Optional[Engine] = None
_is_started = False


def create_db(engine_to_use, name: str):
    with engine_to_use.connect() as conn:
        conn.execute(text("COMMIT"))
        conn.execute(text(f"CREATE DATABASE {name}"))


def drop_db(engine_to_use, db_name: str):
    with engine_to_use.connect() as conn:
        conn.execute(text("COMMIT"))
        conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))


def create_test_database_url(url_to_modify: URL) -> URL:
    """
    Returns a modified URL where the database name is suffixed with _test
    :return:
    """
    return url_to_modify.set(database=url_to_modify.database + "_test")


def init_test_db(db_url: URL, metadata: MetaData, drop_existing=False) -> Engine:
    """
    Connects to the configured database temporarily, issues CREATE commands to instantiate a test database,
    disposes the engine and replaces the global engine with the test one.

    :return: Reference to the instantiated test engine.
    """
    global _engine
    global _is_started

    temp_engine = create_engine(db_url)
    test_db_url = create_test_database_url(db_url)

    if drop_existing is True:
        drop_db(temp_engine, test_db_url.database)

    create_db(temp_engine, test_db_url.database)

    _engine = create_engine(test_db_url)
    metadata.create_all(_engine)
    _is_started = True

    return _engine


def destroy_test_db(db_url):
    """
    If the module's engine is a test engine, it will dispose it.
    Then, connects to the given db_url as "main" database and drops the test database.

    :param db_url:
    :return:
    """
    global _engine
    global _is_started

    if _is_started is True:
        _engine.dispose()

        temp_engine = create_engine(db_url)
        test_db_url = create_test_database_url(db_url)

        drop_db(temp_engine, test_db_url.database)
        _is_started = False

    return
