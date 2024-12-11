default:
    {just_executable()} --list

test:
    python -m pytest
    avdoc tests/example.avsc > out/example.html && open out/example.html
