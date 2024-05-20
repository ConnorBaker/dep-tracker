{ cowsay, dep-tracker-hook }:
cowsay.overrideAttrs (prevAttrs: {
  nativeBuildInputs = prevAttrs.nativeBuildInputs or [ ] ++ [ dep-tracker-hook ];
})
