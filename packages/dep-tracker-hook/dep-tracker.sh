# shellcheck shell=bash

echo "Sourcing dep-tracker" >&2

depTracker() {
  log () { echo "depTracker: $1" >&2 ; }

  log "Executing"

  # TODO: Assumption that the `.lib` output for each dependency is present in the dependency arrays if it is needed.
  #       Don't want to have to figure out a way to recursively search for the `.lib` outputs for each element in
  #       the depedency arrays.

  # These names are all guaranteed to be arrays (though they may be empty), even with __structuredAttrs set.
  local -a dependencyArrayNames=(
    pkgsBuildBuild
    pkgsBuildHost
    pkgsBuildTarget
    pkgsHostHost
    pkgsHostTarget
    pkgsTargetTarget
  )

  local -r depTrackerDir="$(mktemp --directory --tmpdir="$NIX_BUILD_TOP" "dep-tracker-XXXXXX")"
  log "Using $depTrackerDir as the dep-tracker directory" >&2
  mkdir -p "$depTrackerDir"

  # Because the arrays can be arbitrarily long, serialize them into a file and read them back in.
  local -A pythonHookArgs=()
  for dependencyArrayName in "${dependencyArrayNames[@]}"; do
    dependencyArray="${!dependencyArrayName}"

    if [[ -z "${dependencyArray[*]}" ]]; then
      log "Skipping $dependencyArrayName because it is empty" >&2
      continue
    fi

    local filename="$depTrackerDir/dep-tracker-$dependencyArrayName.txt"
    log "Writing $dependencyArrayName to $filename" >&2

    pythonHookArgs["--$dependencyArrayName"]="$filename"
    for dependencyPath in "${dependencyArray[@]}"; do
      echo "$dependencyPath" >> "$filename"
    done

    log "TODO: DEBUGGING: Contents of $filename:" >&2
    cat "$filename" >&2
  done

  dep-tracker --db "$depTrackerDir/dep-tracker.db" "${pythonHookArgs[@]@k}"

  mkdir -p "${out:?}/nix-support"
  cp "$depTrackerDir/dep-tracker.db" "$out/nix-support/dep-tracker.db"
  log "Copied dep-tracker.db to $out/nix-support/dep-tracker.db" >&2

  rm -rf "$depTrackerDir"
  log "Removed $depTrackerDir" >&2
}
postPhases+=(depTracker)
