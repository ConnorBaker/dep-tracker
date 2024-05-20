import sqlite3

from .args import Args, create_arg_parser, transform_cli_args
from .db import (
    log_needs,
    log_provides,
    log_store_entries,
    populate_tables,
    setup_tables,
)
from .utils import dumps_json


def main() -> None:
    args: Args = transform_cli_args(create_arg_parser().parse_args())
    print(dumps_json(args))

    db = sqlite3.connect(args["db"], autocommit=True)
    db.row_factory = sqlite3.Row

    setup_tables(db)
    populate_tables(db, args["deps"])
    log_store_entries(db)
    log_provides(db)
    log_needs(db)


if __name__ == "__main__":
    main()
