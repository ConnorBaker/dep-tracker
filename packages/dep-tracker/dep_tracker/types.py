from collections.abc import Set
from typing import Literal, get_args

PackageSet = Literal[
    "pkgsBuildBuild",
    "pkgsBuildHost",
    "pkgsBuildTarget",
    "pkgsHostHost",
    "pkgsHostTarget",
    "pkgsTargetTarget",
]

PACKAGE_SETS: Set[PackageSet] = set(get_args(PackageSet))

DependencyArrayName = Literal[
    "depsBuildBuild",
    "depsBuildBuildPropagated",
    "depsBuildHost",
    "depsBuildHostPropagated",
    "depsBuildTarget",
    "depsBuildTargetPropagated",
    "depsHostHost",
    "depsHostHostPropagated",
    "depsHostTarget",
    "depsHostTargetPropagated",
    "depsTargetTarget",
    "depsTargetTargetPropagated",
    # Legacy names
    "nativeBuildInputs",
    "propagatedNativeBuildInputs",
    "buildInputs",
    "propagatedBuildInputs",
]

DEPENDENCY_ARRAY_NAMES: Set[DependencyArrayName] = set(get_args(DependencyArrayName))
