import json
import subprocess
from collections.abc import Mapping, Set
from logging import Logger
from pathlib import Path
from sqlite3 import Row
from typing import Any, cast, override

from .logger import get_logger
from .types import DEPENDENCY_ARRAY_NAMES, PACKAGE_SETS, DependencyArrayName, PackageSet

logger: Logger = get_logger(__name__)


class DepTrackerJSONEncoder(json.JSONEncoder):
    @override
    def default(self, o: Any) -> Any:
        match o:
            case Path():
                return o.as_posix()
            case set():
                return sorted(o)  # pyright: ignore[reportUnknownArgumentType,reportUnknownVariableType]
            case Row():
                return dict(o)
            case _:
                return super().default(o)


def dumps_json(obj: Any) -> str:
    return json.dumps(obj, indent=4, sort_keys=True, cls=DepTrackerJSONEncoder)


def get_flake_attr_deps(flake_attr: str) -> Mapping[DependencyArrayName, Set[Path]]:
    proc = subprocess.run(
        [
            "nix",
            "--extra-experimental-features",
            "nix-command flakes",
            "eval",
            "--json",
            flake_attr,
            "--apply",
            f"""
            let
                attrsOfInterest = builtins.fromJSON ''{json.dumps(sorted(DEPENDENCY_ARRAY_NAMES))}'';
                attrsOfInterestAsAttrSet =
                    builtins.listToAttrs
                        (builtins.map (name: {{ inherit name; value = null; }}) attrsOfInterest);
            in
            pkg: builtins.intersectAttrs attrsOfInterestAsAttrSet pkg
            """,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        raise RuntimeError(f"Failed to evaluate expression: {proc.stderr}")

    return {
        dependency_array_name: set(map(Path, dependencies))
        for dependency_array_name, dependencies in json.loads(proc.stdout).items()
    }


def dependency_array_name_to_package_set(dependency_array_name: DependencyArrayName) -> PackageSet:
    if dependency_array_name.startswith("deps"):
        package_set = dependency_array_name.replace("deps", "pkgs", 1).removesuffix("Propagated")
        assert package_set in PACKAGE_SETS
        return cast(PackageSet, package_set)
    elif dependency_array_name in {
        "nativeBuildInputs",
        "propagatedNativeBuildInputs",
    }:
        return "pkgsBuildHost"
    elif dependency_array_name in {
        "buildInputs",
        "propagatedBuildInputs",
    }:
        return "pkgsHostTarget"
    else:
        raise ValueError(f"Unknown dependency array name: {dependency_array_name}")
