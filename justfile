default:
    {{just_executable()}} --list

test:
    pytest
    avdoc tests/example.avsc > out/example.html && open out/example.html

clean:
  rm -r dist/

publish: clean
  # set password to __token__ and use PyPI token
  uv build && uv publish