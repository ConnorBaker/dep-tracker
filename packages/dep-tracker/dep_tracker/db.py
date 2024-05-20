import sqlite3
from collections.abc import Mapping, Set
from logging import Logger
from pathlib import Path

from .deps import get_needs, get_provides
from .logger import get_logger
from .types import PackageSet
from .utils import dumps_json

logger: Logger = get_logger(__name__)


def setup_tables(db: sqlite3.Connection) -> None:
    logger.warning("Creating tables")
    db.executescript(
        # `store_entries` table enumerates all store entries and the package set they belong to
        """
        CREATE TABLE
            store_entries
                ( store_entry TEXT NOT NULL
                , package_set TEXT NOT NULL
                , PRIMARY KEY (store_entry)
                ) STRICT;
        """
        +  # `provides` table maps store entries to relative library paths and names they provide
        """
        CREATE TABLE
            provides
                ( store_entry  TEXT NOT NULL
                , library_path TEXT NOT NULL
                , library_name TEXT NOT NULL
                , PRIMARY KEY (store_entry, library_path, library_name)
                , FOREIGN KEY (store_entry) REFERENCES store_entries(store_entry)
                ) STRICT;
        """
        +  # `needs` table maps store entries to relative library paths and names they need
        """
        CREATE TABLE
            needs
                ( store_entry  TEXT NOT NULL
                , library_path TEXT NOT NULL
                , library_name TEXT NOT NULL
                , PRIMARY KEY (store_entry, library_path, library_name)
                , FOREIGN KEY (store_entry) REFERENCES store_entries(store_entry)
                ) STRICT;
        """
    )
    logger.warning("Tables created")


def populate_tables(db: sqlite3.Connection, deps: Mapping[PackageSet, Set[Path]]) -> None:
    store_entries = {store_entry for store_entries in deps.values() for store_entry in store_entries}

    # Populate `store_entries` table
    db.executemany(
        """
        INSERT INTO
            store_entries
        VALUES
            ( :store_entry
            , :package_set
            )
        """,
        [
            {"store_entry": store_entry.as_posix(), "package_set": package_set}
            for package_set, store_entries in deps.items()
            for store_entry in store_entries
        ],
    )

    # Populate `provides` table
    db.executemany(
        """
        INSERT INTO
            provides
        VALUES
            ( :store_entry
            , :library_path
            , :library_name
            )
        """,
        [provides_entry for store_entry in store_entries for provides_entry in get_provides(store_entry)],
    )

    # Populate `needs` table
    db.executemany(
        """
        INSERT INTO
            needs
        VALUES
            ( :store_entry
            , :library_path
            , :library_name
            )
        """,
        [needs_entry for store_entry in store_entries for needs_entry in get_needs(store_entry)],
    )


def log_store_entries(db: sqlite3.Connection) -> None:
    logger.warning("Logging contents of store_entries")
    for row in db.execute(
        # It is incredibly frustrating to be unable to write the fields as a tuple.
        """
        SELECT
            *
        FROM
            store_entries
        ORDER BY
            store_entry
        """
    ):
        logger.warning("%s", dumps_json(row))


def log_provides(db: sqlite3.Connection) -> None:
    logger.warning("Logging contents of provides")
    for row in db.execute(
        """
        SELECT
            *
        FROM
            provides
        ORDER BY
            store_entry, library_path, library_name
        """
    ):
        logger.warning("%s", dumps_json(row))


def log_needs(db: sqlite3.Connection) -> None:
    logger.warning("Logging contents of needs")
    for row in db.execute(
        """
        SELECT
            *
        FROM
            needs
        ORDER BY
            store_entry, library_path, library_name
        """
    ):
        logger.warning("%s", dumps_json(row))
