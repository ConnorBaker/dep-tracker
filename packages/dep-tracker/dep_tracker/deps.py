import re
import subprocess
from collections.abc import Iterable, Set
from functools import cache
from logging import Logger
from pathlib import Path
from typing import TypedDict

from .logger import get_logger

logger: Logger = get_logger(__name__)


class ProvidesEntry(TypedDict):
    store_entry: str
    library_path: str
    library_name: str


class NeedsEntry(TypedDict):
    store_entry: str
    library_path: str
    library_name: str


# TODO: What if the store path doesn't exist? Do we need to build the entry?


@cache
def get_relative_lib_paths(store_entry: Path) -> Set[Path]:
    """
    Return a set of relative paths to libraries found in the store entry.
    """
    lib_suffix_pattern = re.compile(r"^\.so(?:\.\d+)?$")
    return set(
        path.relative_to(store_entry)
        for path in store_entry.resolve(strict=True).rglob("*.so*")
        if path.is_file() and lib_suffix_pattern.match(path.suffix)
    )


def get_provides(store_entry: Path) -> Iterable[ProvidesEntry]:
    relative_lib_paths: Set[Path] = get_relative_lib_paths(store_entry)
    logger.debug("Found libraries: %s", relative_lib_paths)
    store_entry_str = store_entry.as_posix()
    return [
        {
            "store_entry": store_entry_str,
            "library_path": relative_lib_path.as_posix(),
            "library_name": relative_lib_path.name,
        }
        for relative_lib_path in relative_lib_paths
    ]


def get_needs(store_entry: Path) -> Iterable[NeedsEntry]:
    """
    Return a dictionary mapping relative library paths to library names needed by the path.
    """
    relative_lib_paths: Set[Path] = get_relative_lib_paths(store_entry)
    logger.debug("Found libraries: %s", relative_lib_paths)

    store_entry_str = store_entry.as_posix()
    ret: list[NeedsEntry] = []
    for relative_lib_path in relative_lib_paths:
        lib_path = store_entry / relative_lib_path
        proc = subprocess.run(
            ["patchelf", "--print-needed", lib_path.as_posix()], text=True, check=True, capture_output=True
        )
        dependencies = set(proc.stdout.splitlines())
        logger.debug("Dependencies for %s: %s", relative_lib_path, dependencies)
        for dependency in dependencies:
            ret.append({
                "store_entry": store_entry_str,
                "library_path": relative_lib_path.as_posix(),
                "library_name": dependency,
            })

    return ret
