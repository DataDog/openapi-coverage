"""Calculate coverage for paths."""

from werkzeug.routing import Map, Rule


def build_url_map(schema):
    """Build a map of URL to schema."""
    rules = []
    for path, operations in schema.get("paths", {}).items():
        for method, operation in operations.items():
            rules.append(
                Rule(
                    path.replace("{", "<").replace("}", ">"),
                    methods=[method.upper()],
                    endpoint=("paths", path, method),
                )
            )
            # TODO handle servers

    return Map(rules)


from openapi_coverage.schemas import coverable_parts


def coverable_paths(schema, schema_keys=None):
    """Return schema parts that should be tested."""

    coverage = set()

    for path, operations in schema.get("paths", {}).items():
        for method, operation in operations.items():
            if "parameters" in operation:
                for param in operation["parameters"]:
                    coverage |= coverable_parts(param["schema"], [param["name"]])

    return coverage
