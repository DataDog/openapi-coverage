"""Generage OpenAPI coverage."""

PRIMITIVE_TYPES=["int", "float", "boolean", "string"]

PRIMITIVE_TYPES_CLASSES={
    "int": type(1),
    "float" : type(1.0),
    "boolean": type(True),
    "string": type("hello")
}


def cover_schema(schema, data, schema_keys=None):
    """Cover the schema with the data."""
    schema_keys = schema_keys or []
    type_ = schema.get("type", "object")

    coverage = set()

    if type_ in PRIMITIVE_TYPES:
        coverage.add(("/".join(schema_keys), type(data) == PRIMITIVE_TYPES_CLASSES[type_]))

    elif type_ == "object":
        if "properties" in schema:
            for k in schema["properties"]:
                if k in data:
                    coverage = coverage | cover_schema(schema["properties"][k], data[k], schema_keys + [k])

        if "oneOf" in schema:
            for i, s in enumerate(schema["oneOf"]):
                try:
                    coverage = coverage | cover_schema(s, data, schema_keys + [i])
                except ValueError:
                    pass

        if "additionalProperties" in schema:
            for k in data:
                if k not in schema.get("properties", {}):
                    coverage = coverage | cover_schema(schema["additionalProperties"], data[k], schema_keys + [k])



    elif type_ == "array":
        if "items" in schema:
            for i, d in enumerate(data):
                coverage = coverage | cover_schema(schema["items"], d, schema_keys + [i])

    else:
        # TODO cover minimum, maximum, pattern, etc.

        if "enum" in schema:
            if data not in schema["enum"]:
                raise ValueError(f"{data} is not in {schema['enum']}")

    return coverage
