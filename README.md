avrodoc
=======

Generate human-readable documentation for an Avro schema AVSC file.

```shell
python avdoc.py example.avsc > out/example.html && open out/example.html
```

To provide a version ID, e.g. the current git commit:
```shell
python avdoc.py --schema-version $(git rev-parse --short head) example.avsc > out/example.html
```

This tool is intended as a replacement for [avrodoc-plus](https://github.com/mikaello/avrodoc-plus).
To run `avrodoc-plus` and see it's output:

```shell
npm install
node_modules/@mikaello/avrodoc-plus/bin/avrodoc-plus.js example.avsc --output out/avrodocplus.html
```
