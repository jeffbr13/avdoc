avdoc
=====

CLI tool to generate human-readable HTML documentation for an [Apache Avro] schema AVSC file.

Want Avro schema docs? 'avdoc!

## Installation

### Requirements
Software required outside of Python package dependencies:
- [Graphviz] for the reference graph.

### Install as Python package
Install the [`avdoc` package on PyPI]:
```shell
pip install --upgrade avdoc
```

## Usage

```shell
[python -m] avdoc tests/example.avsc > out/example.html && open out/example.html
```

To provide a version ID, e.g. the current git commit:
```shell
[python -m] avdoc --schema-version $(git rev-parse --short head) example.avsc > out/example.html
```

`$ avdoc --help`
```
usage: avdoc [-h] [--schema-title SCHEMA_TITLE]
             [--schema-version SCHEMA_VERSION]
             avsc

CLI tool to generate HTML documentation for an Apache Avro schema

positional arguments:
  avsc

options:
  -h, --help            show this help message and exit
  --schema-title SCHEMA_TITLE
  --schema-version SCHEMA_VERSION
```

## Features
- [x] graph/diagram of which record schemas reference each other
- [x] Markdown support in `"doc"` strings
- [ ] supports all [complex Avro types][]
  - [x] record
  - [x] enum
  - [x] array
  - [x] union
  - [ ] error
  - [ ] map
  - [ ] request

### Design Goals
The output should:
- be well-formatted semantic HTML.
- be legible in basic browsers without styling.
- aid understanding of the underlying schema.
- be a single static file for sharing without dependencies.
- be linkable to reference specific schemas and fields.



## Development
- [devenv] for development environment
- [direnv] for automatic shell activation (optional)

`devenv shell` should set up Python & Poetry with dependencies installed.
Use `.venv/bin/python` as your Python interpreter.

### Publishing

#### Bump version

```shell
bumpversion major|minor|patch
```

#### Update documentation
Run `mdsh`.

#### Publish Python package to PyPI
[Configure Poetry credentials] with [PyPI token] and run:
```shell
poetry publish --build
```

### Architecture
Not much to speak of. 

`avdoc` is a couple of hundred lines of Python script
generating static HTML, with a bit of string munging to get component outputs
into the final HTML output page. 
This code is purpose-oriented.
The output is opinionated, but not much time has been spent on the code
past getting it working for my own needs.
It's not intended to be exemplary of anything in particular.


## Maintenance
I probably won't pay too much attention to `avdoc` maintenance 
once it's suitable for my own needs.
I'd like to try to ensure that dependencies are kept up to date.

Fork for your own needs.
Raise a PR if you'd like me to consider including your changes.
Make sure you adhere to the [license](#license) by ensuring your users
have access to your modifications.

## License
[AGPL]:
> [[…] requires the operator of a network server to provide the source code of the modified version running there to the users of that server. Therefore, public use of a modified version, on a publicly accessible server, gives the public access to the source code of the modified version.](https://www.gnu.org/licenses/agpl-3.0.html#:~:text=It%20requires%20the%20operator%20of%20a%20network%20server)

`avdoc` is released as copyleft software.
If you modify `avdoc` then you must make changes available to your users.

If the AGPL license is an issue, and you want to relicense `avdoc` privately, 
then reach out to discuss pricing. 

## Prior Art

`avdoc` is intended as a replacement for [avrodoc-plus],
which itself was intended as a replacement for [avrodoc],
via a long line of forks.

To run `avrodoc-plus` and see its output:

```shell
npm install @mikaello/avrodoc-plus
node_modules/@mikaello/avrodoc-plus/bin/avrodoc-plus.js example.avsc --output out/avrodocplus.html
```

## Why?

Unfortunately the original [avrodoc] and forks are all
in varying stages of [software decay], mostly due to NodeJS ecosystem churn. 
Their NPM package dependencies include packages which have themselves 
gone unmaintained or had breaking changes in following versions, 
with CVEs piling up against the transitive dependencies.
[avrodoc-plus] has about 10 critical CVEs in its dependency graph.
This isn't necessarily an issue in itself unless you're running these
avrodoc tools in an online capacity or on untrusted input.
But at $WORK it was generating a lot of false-positives in automatic
[SBOM] security scanners which had to be explained to infosec specialists.

The HTML output from the avrodoc tools is also rather dynamic, 
requiring JS to render, when it could just be a classic HTML page. 

I have taken the opportunity to implement some quality-of-life
improvements for readers.
See [§Design Goals](#design-goals) for more info. 

Why the name `avdoc` specifically?
The [Apache Software Foundation protects project name trademarks]
(quite rightly) and I wanted to avoid the [kcat naming issue].

`avdoc` is "Powered by Apache Avro™" but not a part of Apache Avro™.



[//]: # (Links)
[Apache Avro]: https://avro.apache.org
[complex Avro types]: https://avro.apache.org/docs/1.11.1/specification/#complex-types-1
[avrodoc-plus]: https://github.com/mikaello/avrodoc-plus
[avrodoc]: https://github.com/ept/avrodoc
[AGPL]: https://www.gnu.org/licenses/agpl-3.0.html
[direnv]: https://direnv.net
[devenv]: https://devenv.sh
[Graphviz]: https://www.graphviz.org
[software decay]: https://en.wikipedia.org/wiki/Software_rot
[SBOM]: https://en.wikipedia.org/wiki/Software_supply_chain
[kcat naming issue]: https://github.com/edenhill/kcat#what-happened-to-kafkacat
[Apache Software Foundation protects project name trademarks]: https://www.apache.org/foundation/marks/faq/#products
[Configure Poetry credentials]: https://python-poetry.org/docs/repositories/#configuring-credentials
[PyPI token]: https://pypi.org/help/#apitoken
[`avdoc` package on PyPI]: https://pypi.org/project/avdoc/
