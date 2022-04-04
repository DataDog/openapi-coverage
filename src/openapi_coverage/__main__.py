import click
import yaml
from jsonref import JsonRef

from .har import cover_har, load_har
from .loader import yaml
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
@click.option("--output", "-o", type=click.Path(), default="-")
def cover(schema_path, har_paths, output):
    with open(schema_path) as f:
        schema = JsonRef.replace_refs(yaml.load(f))

    coverred = set()
    url_map = build_url_map(schema)

    for har_path in har_paths:
        har = load_har(har_path)
        coverred |= {
            replace_refs(schema, c) for c in cover_har(schema, har, url_map=url_map)
        }

    coverable = {replace_refs(schema, c) for c in coverable_paths(schema)}
    coverable_trie = build_trie(coverable)
    coverred_trie = build_trie(coverred)

    # for c in sorted({replace_refs(schema, c) for c in coverred}):
    #     print(c)

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
    
    for missing in coverable - coverred:
        value = lookup(schema, missing)
        try:
            print(f"{missing} - {value.lc.line}: {value.lc.col}") 
        except:
            print(f"{missing} - {value}")
            raise
        while False and missing:
            value = lookup(schema, missing)
            try:
                print(f"{missing} - {value.lc.line}: {value.lc.col}")
                break
            except AttributeError:
                missing = missing[:-1]


if __name__ == "__main__":
    cli()
