# avdoc
# Copyright (C) 2023 Ben Jeffrey
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""CLI tool to generate HTML documentation for an Apache Avro schema
"""
import argparse
import json
import logging
import re
from datetime import datetime
from datetime import timezone
from io import BytesIO
from pathlib import Path

import dominate
import avro.schema
import avro.name
import avro.errors
import mistune
import pygraphviz
from dominate.tags import *
from dominate.tags import main as dom_main
from dominate.util import raw, text

from . import __version__


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
logger = logging.getLogger(__name__)


def avro_type_specification_url(logical_type_name: str) -> str:
    return {
        "decimal": "https://avro.apache.org/docs/1.11.1/specification/#decimal",
        "uuid": "https://avro.apache.org/docs/1.11.1/specification/#uuid",
        "date": "https://avro.apache.org/docs/1.11.1/specification/#date",
        "time-millis": "https://avro.apache.org/docs/1.11.1/specification/#time-millisecond-precision",
        "time-micros": "https://avro.apache.org/docs/1.11.1/specification/#time-microsecond-precision",
        "timestamp-millis": "https://avro.apache.org/docs/1.11.1/specification/#timestamp-millisecond-precision",
        "timestamp-micros": "https://avro.apache.org/docs/1.11.1/specification/#timestamp-microsecond-precision",
        "local-timestamp-millis": "https://avro.apache.org/docs/1.11.1/specification/#local-timestamp-millisecond-precision",
        "local-timestamp-micros": "https://avro.apache.org/docs/1.11.1/specification/#local-timestamp-microsecond-precision",
        "duration": "https://avro.apache.org/docs/1.11.1/specification/#duration",
        "record": "https://avro.apache.org/docs/1.11.1/specification/#schema-record",
        "enum": "https://avro.apache.org/docs/1.11.1/specification/#enums",
        "array": "https://avro.apache.org/docs/1.11.1/specification/#arrays",
        "map": "https://avro.apache.org/docs/1.11.1/specification/#maps",
        "union": "https://avro.apache.org/docs/1.11.1/specification/#unions",
        "fixed": "https://avro.apache.org/docs/1.11.1/specification/#fixed",
    }[logical_type_name]


def parse(json_string: str) -> avro.name.Names:
    """Parse Avro schema for Names used."""
    try:
        json_data = json.loads(json_string)
    except json.decoder.JSONDecodeError as e:
        raise avro.errors.SchemaParseException(
            f"Error parsing JSON: {json_string}, error = {e}"
        ) from e
    names = avro.name.Names()
    avro.schema.make_avsc_object(json_data, names, validate_enum_symbols=True)
    return names


def field_type_html(field_schema: avro.schema.Schema):
    _span = span(__pretty=False, _class="type")
    with _span:
        match field_schema:
            case avro.schema.NamedSchema(fullname=fullname):
                a(fullname, href=f"#{fullname}")
                # sup(f"{field_schema.type}")
            case avro.schema.ArraySchema(items=items):
                a("array", href=avro_type_specification_url("array"))
                text("[")
                field_type_html(items)
                text("]")
            case avro.schema.UnionSchema(schemas=schemas):
                a("union", href=avro_type_specification_url("union"))
                text("[")
                for i, s in enumerate(schemas):
                    if i != 0:
                        text("|")
                    field_type_html(s)
                text("]")
            case avro.schema.LogicalSchema(logical_type=logical_type):
                a(logical_type, href=avro_type_specification_url(logical_type))
                # sup(f"{field_schema.type}")
            case avro.schema.Schema(type=t):  # catch-all
                text(t)
            # TODO: cases for RPC types?
            #       - error
            #       - map
            #       - request
    return _span


def field_html(field: avro.schema.Field, schema_name: str) -> dom_tag:
    field_id = f"{schema_name}.{field.name}"
    field_docstring = getattr(field, "doc", None)
    field_docstring = (
        raw(mistune.html(field_docstring)) if field_docstring else i("missing")
    )
    field_default = (
        (samp("null") if field.default is None else field.default)
        if field.has_default
        else ""
    )
    return tr(
        th(
            a(field.name, _class="fieldname", id=field_id, href=f"#{field_id}"),
            scope="row",
        ),
        td(field_docstring),
        td(field_type_html(field.type)),
        td(field_default),
    )


def named_schema_html(schema: avro.schema.NamedSchema) -> dom_tag:
    schema_docstring = getattr(schema, "doc", None)
    schema_docstring = (
        raw(mistune.html(schema_docstring)) if schema_docstring else i("missing")
    )

    _section = section(id=schema.fullname, _class="schema")
    with _section:
        with h2():
            a(schema.fullname, href=f"#{schema.fullname}")
            small(a(f"{schema.type}", href=avro_type_specification_url(schema.type)))

        h3("doc")
        p(schema_docstring, _class="docstring")

        match schema:
            case avro.schema.EnumSchema(symbols=symbols):
                with ul("One of:"):
                    for symbol in symbols:
                        li(samp(symbol))
            case avro.schema.RecordSchema(fields=fields):
                h3("fields")
                with table(_class=".fullbleed"):
                    thead(
                        tr(
                            th("name"),
                            th("doc"),
                            th("type"),
                            th("default"),
                        )
                    )
                    for field in fields:
                        field_html(field, schema.fullname)
                    thead(
                        tr(
                            th("name"),
                            th("doc"),
                            th("type"),
                            th("default"),
                        )
                    )
            case avro.schema.FixedSchema(size=size):
                p(f"Fixed type {size} bytes in size.")
    return _section


def generate_html(
    names: avro.name.Names,
    dependency_graph_svg: str,
    schema_filename: str,
    schema_title=None,
    schema_version=None,
) -> str:
    # TODO: pass through title from CLI
    # TODO: pass "doc" fields through pandoc if it exists
    page_title = f"{schema_title or schema_filename} (avdoc)"
    document = dominate.document(title=page_title)
    with document.head:
        meta(charset="utf-8")
        meta(name="viewport", content="width=device-width, initial-scale=1.0")
        # TODO: custom stylesheet
        link(
            rel="stylesheet",
            href="https://unpkg.com/missing.css@1.0.9/dist/missing.min.css",
        )
        # TODO: custom styles
        # Custom formatting:
        # - wider page
        # - full-width & striped tables
        # - quieter links to schema fieldnames in tables
        style(
            raw(
                """
                :root {
                    --line-length: 80rem;
                }
                th, td {
                    padding: 0.25rem;
                }
                /* striped table */
                tbody tr:nth-child(even) {
                    background-color: var(--plain-bg);
                }
                /* field names should match table text */
                th a.fieldname {
                    color: var(--plain-fg);
                    text-decoration-line: none;
                }
                """
            )
        )
    with document.body:
        with dom_main():
            header(h1(schema_title or page_title))
            with figure():
                figcaption("reference graph")
                raw(dependency_graph_svg)
            for name, schema in names.names.items():
                named_schema_html(schema)
            with footer():
                now = datetime.now(tz=timezone.utc)
                p("Schema filename: ", code(schema_filename), id="schema-filename")
                if schema_version:
                    p("Schema version: ", code(schema_version), id="schema-version")
                p(
                    "⏲ ",
                    time_(now.strftime("%c"), datetime=now.isoformat()),
                    _id="generation-time",
                )
                with p(_id="credits"):
                    text("⚒ generated by ")
                    a("avdoc", href="https://pypi.org/project/avdoc/")
                    text(f" version {__version__} ")
                    text("© Ben Jeffrey 2023. Released under the ")
                    a("AGPL", href="https://www.gnu.org/licenses/agpl-3.0.html")
                    text(".")
    return document.render()


def get_edges(schema: avro.schema.Schema):
    edges = []
    match schema:
        case avro.schema.RecordSchema(fullname=name, fields=fields):
            for field in fields:
                match field.type:
                    case avro.schema.NamedSchema(fullname=field_name):
                        edges.append((name, field_name))
                    case avro.schema.ArraySchema(items=items):
                        edges.append((name, items.fullname)) if isinstance(
                            items, avro.schema.NamedSchema
                        ) else ...
                    case avro.schema.UnionSchema(schemas=field_schemas):
                        for s in field_schemas:
                            edges.append((name, s.fullname)) if isinstance(
                                s, avro.schema.NamedSchema
                            ) else ...
    return edges


def draw_graph(names: avro.name.Names):
    vertices = names.names.keys()
    edges = []
    for name, schema in names.names.items():
        edges.extend(get_edges(schema))
    G = pygraphviz.AGraph(directed=True)
    for v in vertices:
        G.add_node(v, href=f"#{v}")
    for e in edges:
        G.add_edge(*e)
    G.layout("dot")
    buffer = BytesIO()
    G.draw(buffer, format="svg")  # NOTE: looks like path can be a file
    buffer.seek(0)
    svg_str = buffer.read().decode("utf-8")
    # replace fixed width with relative width
    return re.sub(r'svg width="\d+pt"', 'svg width="100%"', svg_str)


def avdoc(avsc: Path, schema_title=None, schema_version=None) -> str:
    avsc_contents: str = avsc.read_text(encoding="utf-8")
    names = parse(avsc_contents)
    dependency_graph_svg = draw_graph(names)
    html = generate_html(
        names,
        dependency_graph_svg,
        schema_filename=avsc.name,
        schema_title=schema_title,
        schema_version=schema_version,
    )
    return html


def main():
    """Run as CLI app"""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("avsc", type=Path)
    parser.add_argument("--schema-title", default="")
    parser.add_argument("--schema-version", default="")
    args = parser.parse_args()
    html = avdoc(args.avsc, args.schema_title, args.schema_version)
    print(html)


if __name__ == "__main__":
    main()
