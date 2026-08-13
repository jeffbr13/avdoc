{pkgs, ...}: {
  # https://devenv.sh/basics/
  #  env.GREET = "devenv";

  # https://devenv.sh/packages/
  packages = with pkgs; [
    graphviz
    mdsh
  ];

  # https://devenv.sh/tests/
  enterTest = ''
    avdoc --help
    pytest
  '';

  # https://devenv.sh/scripts/
  #  scripts.hello.exec = "echo hello from $GREET";

  # https://devenv.sh/tasks/#entershell-entertest
  enterShell = ''
    # Create a symlink to the Python virtual environment for IDE compatibility
    if [ ! -L "$DEVENV_ROOT/venv" ]; then
        ln -s "$DEVENV_STATE/venv/" "$DEVENV_ROOT/venv"
    fi
  '';

  # https://devenv.sh/languages/
  # languages.nix.enable = true;
  languages.python = {
    enable = true;
    venv.enable = true;
    uv = {
      enable = true;
      sync = {
        enable = true;
        allGroups = true;
      };
    };
  };

  languages.javascript.enable = true;

  # https://devenv.sh/pre-commit-hooks/
  git-hooks = {
    enable = true;
    package = pkgs.prek;
    hooks = {
      alejandra.enable = true; # nix formatter
      statix.enable = true; # nix linter
      ruff.enable = true; # python linter
      ruff-format.enable = true; # python formatter
      shfmt.enable = true; # shell formatter
      shellcheck.enable = true; # shell linter
      typos.enable = true; # source code spellchecker
      mdsh.enable = true; # documentation generator
    };
  };
  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";

  # See full reference at https://devenv.sh/reference/options/
}
