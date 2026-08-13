default:
    {{just_executable()}} --list

test:
    devenv test

preview:
    avdoc tests/example.avsc > out/example.html && open out/example.html

clean:
  rm -r dist/

publish: clean
  # set password to __token__ and use PyPI token
  uv build && uv publish