"""Calculate coverage for paths."""

from werkzeug.routing import Map, Rule


def build_url_map(schema):
    """Build a map of URL to schema."""
    rules = []
    for path, operations in schema.get("paths", {}).items():
        for method, operation in operations.items():
            rules.append(Rule(
                path.replace("{", "<").replace("}", ">"),
                methods=[method.upper()],
                endpoint=("paths", path, method),
                # endpoint=operation,
            ))
            # TODO handle servers

    return Map(rules)