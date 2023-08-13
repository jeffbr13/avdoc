{pkgs, ...}: {
  # https://devenv.sh/basics/
  #  env.GREET = "devenv";

  # https://devenv.sh/packages/
  packages = [
    pkgs.black
    pkgs.ruff
    pkgs.graphviz
    pkgs.mdsh
  ];

  # https://devenv.sh/scripts/
  #  scripts.hello.exec = "echo hello from $GREET";

  #  enterShell = ''
  #    hello
  #    git --version
  #  '';

  # https://devenv.sh/languages/
  # languages.nix.enable = true;
  languages.python = {
    enable = true;
    poetry.enable = true;
  };

  languages.javascript.enable = true;

  # https://devenv.sh/pre-commit-hooks/
  pre-commit.hooks = {
    alejandra.enable = true; # nix formatter
    statix.enable = true; # nix linter
    black.enable = true; # python formatter
    ruff.enable = true; # python linter
    shfmt.enable = true; # shell formatter
    shellcheck.enable = true; # shell linter
    typos.enable = true; # source code spellchecker
  };
  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";

  # See full reference at https://devenv.sh/reference/options/
}
