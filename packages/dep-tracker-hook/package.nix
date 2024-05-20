{
  lib,
  makeSetupHook,
  dep-tracker,
}:
let
  inherit (lib.maintainers) connorbaker;
in
makeSetupHook {
  name = "dep-tracker-hook";
  propagatedBuildInputs = [ dep-tracker ];
  passthru.provides.setupHook = true;
  meta = {
    description = "temp";
    homepage = "https://github.com/connorbaker/temp";
    maintainers = [ connorbaker ];
  };
} ./dep-tracker.sh
