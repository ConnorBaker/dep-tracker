{ lib, python312Packages }:
let
  callPackage = lib.trivial.flip python312Packages.callPackage { };
in
callPackage (
  {
    buildPythonPackage,
    lib,
    # nativeBuildInputs
    flit-core,
    makeWrapper,
    # buildInputs
    nix,
    patchelf,
    sqlite,
    # passthru.optional-dependencies.dev
    pyright,
    ruff,
  }:
  let
    toModuleName = builtins.replaceStrings [ "-" ] [ "_" ];
    moduleName = toModuleName finalAttrs.pname;
    finalAttrs = {
      pname = "dep-tracker";
      version = "0.1.0";
      format = "pyproject";
      src = lib.sources.sourceByRegex ./. [
        "${moduleName}(:?/.*)?"
        "pyproject.toml"
      ];
      nativeBuildInputs = [
        flit-core
        makeWrapper
      ];
      nativeCheckInputs = [
        pyright
        ruff
      ];
      buildInputs = [
        nix
        patchelf
        sqlite
      ];
      passthru.optional-dependencies.dev = [
        pyright
        ruff
      ];
      doCheck = true;
      checkPhase =
        # preCheck
        ''
          runHook preCheck
        ''
        # Check with ruff
        + ''
          echo "Linting with ruff"
          ruff check
          echo "Checking format with ruff"
          ruff format --diff
        ''
        # Check with pyright
        + ''
          echo "Typechecking with pyright"
          pyright --warnings
          echo "Verifying type completeness with pyright"
          pyright --verifytypes ${moduleName} --ignoreexternal
        ''
        # postCheck
        + ''
          runHook postCheck
        '';
      postInstall = ''
        wrapProgram "$out/bin/dep-tracker" \
          --prefix PATH : ${nix}/bin \
          --prefix PATH : ${patchelf}/bin \
          --prefix PATH : ${sqlite}/bin
      '';
      meta = {
        description = "Tracking dependencies on libraries in Nix builds";
        homepage = "https://github.com/ConnorBaker/${finalAttrs.pname}";
        maintainers = with lib.maintainers; [ connorbaker ];
        mainProgram = "dep-tracker";
      };
    };
  in
  buildPythonPackage finalAttrs
)
