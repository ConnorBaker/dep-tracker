from argparse import ArgumentParser, Namespace
from collections import defaultdict
from collections.abc import Mapping, Set
from logging import Logger
from pathlib import Path
from typing import TypedDict

from .logger import get_logger
from .types import PACKAGE_SETS, PackageSet
from .utils import dependency_array_name_to_package_set, get_flake_attr_deps

logger: Logger = get_logger(__name__)


class Args(TypedDict):
    db: Path
    flake_attr: None | str
    deps: Mapping[PackageSet, Set[Path]]


def create_arg_parser() -> ArgumentParser:
    """
    Creates a database of dependencies in the project
    """
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        help="Path to the database file",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--flake-attr",
        help="A flake attribute to use instead of files containing dependencies",
        required=False,
        type=str,
        default=None,
    )
    for dep_type in PACKAGE_SETS:
        parser.add_argument(
            f"--{dep_type}",
            help=f"File containing all dependencies in {dep_type} delimited by newlines",
            required=False,
            type=Path,
            default=None,
        )
    return parser


def transform_cli_args(args: Namespace) -> Args:
    """
    Verify the arguments
    """

    deps: dict[PackageSet, Set[Path]] = defaultdict(set)
    if args.flake_attr is not None:
        logger.info("Using flake attribute: %s", args.flake_attr)
        for dependency_array_name, dependencies in get_flake_attr_deps(args.flake_attr).items():
            package_set = dependency_array_name_to_package_set(dependency_array_name)
            deps[package_set] |= dependencies
    else:
        for package_set in PACKAGE_SETS:
            # Dependencies are in the form of a file with each dependency on a new line
            dep_file: None | Path = getattr(args, package_set)

            if dep_file is None:
                logger.warning("No file provided for %s", package_set)
                continue

            if not (dep_file.exists() and dep_file.is_file()):
                logger.warning("File for %s does not exist: %s", package_set, dep_file)
                continue

            dep_paths = set(map(Path, dep_file.read_text().splitlines()))

            if not dep_paths:
                logger.warning("No dependencies found for %s", package_set)
                continue

            deps[package_set] = dep_paths

    return {
        "db": args.db,
        "flake_attr": args.flake_attr,
        "deps": deps,
    }
