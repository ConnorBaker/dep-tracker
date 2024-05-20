# dep-tracker

A simple tool to help track library dependencies in a project.

## Usage

Generate a database for the dependencies of OpenCV with:

```bash
nix run .#dep-tracker -- --db opencv.db --flake-attr .#opencv
```

TODO:

- [ ] Recurse into dependencies to get the full closure
- [ ] Detect multiple versions of the same library in a closure (diamond dependencies)
- [ ] Detect libraries that are not in the closure
