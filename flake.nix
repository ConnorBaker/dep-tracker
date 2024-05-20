{
  inputs = {
    flake-parts = {
      inputs.nixpkgs-lib.follows = "nixpkgs";
      url = "github:hercules-ci/flake-parts";
    };
    nixpkgs.url = "github:nixos/nixpkgs";
    git-hooks-nix = {
      inputs = {
        nixpkgs-stable.follows = "";
        nixpkgs.follows = "nixpkgs";
      };
      url = "github:cachix/git-hooks.nix";
    };
    treefmt-nix = {
      inputs.nixpkgs.follows = "nixpkgs";
      url = "github:numtide/treefmt-nix";
    };
  };

  nixConfig = {
    extra-substituters = [
      "https://cantcache.me/cuda"
      "https://cuda-maintainers.cachix.org"
    ];
    extra-trusted-substituters = [
      "https://cantcache.me/cuda"
      "https://cuda-maintainers.cachix.org"
    ];
    extra-trusted-public-keys = [
      "cuda:NtbpAU7XGYlttrhCduqvpYKottCPdWVITWT+3nFVTBY="
      "cuda-maintainers.cachix.org-1:0dq3bujKpuEPMCX6U4WylrUDZ9JyUG0VpVZa7CNfq5E="
    ];
  };

  outputs =
    inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "aarch64-linux"
        "x86_64-linux"
      ];
      imports = [
        inputs.treefmt-nix.flakeModule
        inputs.git-hooks-nix.flakeModule
      ];
      perSystem =
        {
          config,
          inputs',
          lib,
          pkgs,
          ...
        }:
        {
          legacyPackages = pkgs;
          devShells = {
            dep-tracker = pkgs.mkShell {
              strictDeps = true;
              inputsFrom = [ config.packages.dep-tracker ];
              packages = config.packages.dep-tracker.optional-dependencies.dev;
            };
            default = config.devShells.dep-tracker;
          };

          packages =
            let
              inherit (lib.attrsets) filterAttrs isDerivation;
              inherit (lib.customisation) makeScope;
              inherit (lib.filesystem) packagesFromDirectoryRecursive;
              inherit (pkgs) newScope;

              scope = makeScope newScope (
                final:
                packagesFromDirectoryRecursive {
                  inherit (final) callPackage;
                  directory = ./packages;
                }
              );

              packagesOnly = filterAttrs (_: isDerivation) scope;
            in
            packagesOnly;
          pre-commit.settings.hooks =
            let
              # We need to provide wrapped version of mypy and pyright which can find our imports.
              # TODO: The script we're sourcing is an implementation detail of `mkShell` and we should
              # not depend on it exisitng. In fact, the first few lines of the file state as much
              # (that's why we need to strip them, sourcing only the content of the script).
              wrapper =
                name:
                pkgs.writeShellScript name ''
                  source <(sed -n '/^declare/,$p' ${config.devShells.nix-cuda-test})
                  ${name} "$@"
                '';
            in
            {
              # Formatter checks
              treefmt = {
                enable = true;
                package = config.treefmt.build.wrapper;
              };

              # Nix checks
              deadnix.enable = true;
              nil.enable = true;
              statix.enable = true;

              # Python checks
              pyright = {
                enable = true;
                settings.binPath = "${wrapper "pyright"}";
              };
              ruff.enable = true; # Ruff both lints and checks sorted imports
            };

          treefmt = {
            projectRootFile = "flake.nix";
            programs = {
              # Markdown, YAML, JSON
              prettier = {
                enable = true;
                includes = [
                  "*.json"
                  "*.md"
                  "*.yaml"
                ];
                settings = {
                  embeddedLanguageFormatting = "auto";
                  printWidth = 120;
                  tabWidth = 2;
                };
              };

              # Nix
              nixfmt = {
                enable = true;
                package = pkgs.nixfmt-rfc-style;
              };

              # Python
              ruff.enable = true;

              # Shell
              shellcheck.enable = true;

              # TODO: https://github.com/mvdan/sh/issues/921 broken with `@k` in `shfmt`
              # shfmt.enable = true;
            };
          };
        };
    };
}
