import json

import click
import yaml
from jsonref import JsonRef
from yaml import CSafeLoader

from .har import cover_har, load_har
from .loader import PositionLoader
from .lookup import lookup, lookup_endline
from .paths import build_url_map, coverable_paths
from .refs import replace_refs
from .trie import build_trie


@click.group()
def cli():
    """Calculate coverage for OpenAPI files."""
    pass


@cli.command()
@click.argument("schema_path", type=click.Path(exists=True))
@click.argument("har_paths", nargs=-1, type=click.Path(exists=True))
@click.option("--report", "-r", type=click.File(mode="w"), default="-")
@click.option("--stats/--no-stats", "show_stats", default=False)
def cover(schema_path, har_paths, report, show_stats):
    with open(schema_path) as f:
        schema = JsonRef.replace_refs(yaml.load(f, Loader=CSafeLoader))

    coverred = set()
    url_map = build_url_map(schema)

    for har_path in har_paths:
        har = load_har(har_path)
        coverred |= {
            replace_refs(schema, c) for c in cover_har(schema, har, url_map=url_map)
        }

    coverable = {replace_refs(schema, c) for c in coverable_paths(schema)}

    if show_stats:
        coverable_trie = build_trie(coverable)
        coverred_trie = build_trie(coverred)

        stats = []
        for operation in sorted({p[:3] for p in coverable}):
            c = coverred_trie.count_leafs(operation)
            ca = coverable_trie.count_leafs(operation)
            if c > 0 and ca > 0:
                r = 100.0 * c / ca
            else:
                r = 0
            stats.append((r, operation[1:]))

        stats.sort(reverse=True)
        for r, operation in stats:
            click.echo(f"{r:>6.2f}% - {operation}")

        total_coverage = 100.0 * len(coverred) / len(coverable)
        click.echo(f"{total_coverage:>6.2f}% - Total coverage")

    coverred_paths = {
        "version": "1",
        "missing": [list(c) for c in coverable - coverred],
    }
    json.dump(coverred_paths, report, indent=2)


@cli.command()
@click.argument("schema_paths", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["github", "errorformat"]),
    default="errorformat",
)
@click.option("--report", "-r", type=click.Path(), default="-")
def annotate(schema_paths, format, report):
    """Annotate schemas with coverage information."""
    with open(report) as f:
        report = json.load(f)

    missing_paths = report.get("missing", [])

    def format_path(path):
        output = "#"
        for p in path:
            if isinstance(p, int):
                output += f"[{p}]"
            else:
                output += f"/{p}"
        return output

    formats = {
        "github": "::error file={schema_path},line={line},col={column},"
        "title=Coverage::Missing coverage for {missing_path}",
        "errorformat": "{schema_path}:{line}:{column}: "
        "[openapi-coverage] Missing coverage for {missing_path}",
    }

    for schema_path in schema_paths:
        with open(schema_path) as f:
            schema = PositionLoader(f.read()).get_single_data()

        for missing in missing_paths:
            key = (
                *missing[:-1],
                missing[-1] * 2 + 1
                if isinstance(missing[-1], int)
                else "__position__" + str(missing[-1]),
            )
            try:
                value = lookup(schema, key)
                click.echo(
                    formats[format].format(
                        schema_path=schema_path,
                        line=value["line"],
                        column=value["column"],
                        missing_path=format_path(missing),
                    )
                )
            except (RuntimeError, KeyError):
                pass


@cli.command()
@click.argument("schema_paths", nargs=-1, type=click.Path(exists=True))
@click.option("--report", "-r", type=click.Path(), default="-")
@click.option("--summary", "-s", type=click.File(mode="w"), default="-")
def line_list(schema_paths, report, summary):
    with open(report) as f:
        report = json.load(f)

    missing_paths = report.get("missing", [])
    result = {}
    for schema_path in schema_paths:
        with open(schema_path) as f:
            total_lines = 0
            for line in f.readlines():
                total_lines += 1
            f.seek(0)
            schema = PositionLoader(f).get_single_data()

        result[schema_path] = set()

        for missing in missing_paths:
            key = [elt * 2 + 1 if isinstance(elt, int) else elt for elt in missing]
            if isinstance(key[-1], str):
                key[-1] = f"__position__{key[-1]}"
            try:
                value = lookup(schema, key)
            except (RuntimeError, KeyError):
                pass
            else:
                endline = lookup_endline(schema, missing, total_lines)
                result[schema_path].update(range(value["line"], endline + 1))
        result[schema_path] = list(result[schema_path])
        result[schema_path].sort()
    json.dump(result, summary, indent=2)


if __name__ == "__main__":
    cli()
