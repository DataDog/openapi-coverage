import json

import click
import yaml
from jsonref import JsonRef
from yaml import CSafeLoader

from .har import cover_har, load_har
from .loader import PositionLoader
from .lookup import lookup
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
            c = coverred_trie.count_children(operation)
            ca = coverable_trie.count_children(operation)
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
@click.option("--report", "-r", type=click.Path(), default="-")
def annotate(schema_paths, report):
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
                    f"::error file={schema_path},line={value['line']},col={value['column']},"
                    f"title=Coverage::Missing coverage for {format_path(missing)}"
                )
            except (RuntimeError, KeyError):
                pass


if __name__ == "__main__":
    cli()
