"""Calculate coverage for paths."""

from werkzeug.routing import Map, Rule

from openapi_coverage.schemas import coverable_parts


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


def coverable_paths(schema):
    """Return schema parts that should be tested."""
    refs = set()
    coverage = set()

    for path, operations in schema.get("paths", {}).items():
        for method, operation in operations.items():
            prefix = ["paths", path, method]
            for i, parameter in enumerate(operation.get("parameters", [])):
                coverage |= coverable_parts(
                    parameter["schema"],
                    schema_keys=prefix + ["parameters", i, "schema"],
                    refs=refs,
                )

            if "requestBody" in operation and "content" in operation["requestBody"]:
                for content_type, body in operation["requestBody"]["content"].items():
                    coverage |= coverable_parts(
                        body["schema"],
                        schema_keys=prefix
                        + ["requestBody", "content", content_type, "schema"],
                        refs=refs,
                    )

            for status_code, response in operation.get("responses", {}).items():
                for content_type, content in response.get("content", {}).items():
                    coverage |= coverable_parts(
                        content["schema"],
                        schema_keys=prefix
                        + ["responses", status_code, "content", content_type, "schema"],
                        refs=refs,
                    )

    return coverage
