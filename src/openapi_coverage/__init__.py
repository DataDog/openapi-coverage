"""Generage OpenAPI coverage."""

PRIMITIVE_TYPES_CLASSES={
    "integer": type(1),
    "number" : type(1.0),
    "boolean": type(True),
    "string": type("hello")
}


def coverable_parts(schema, schema_keys=None):
    """Return schema parts that should be tested."""
    schema_keys = schema_keys or []
    type_ = schema.get("type", "object")

    coverage = set()

    if type_ == "object":
        if "properties" in schema:
            for k in schema["properties"]:
                print(k)
                coverage |= coverable_parts(schema["properties"][k], schema_keys + [k])
                print(coverage)

        if "oneOf" in schema:
            for i, s in enumerate(schema["oneOf"]):
                coverage |= coverable_parts(s, schema_keys + [i])

        if "additionalProperties" in schema:
            coverage |= coverable_parts(schema["additionalProperties"], schema_keys + ["additionalProperties"])

    elif type_ == "array":
        if "items" in schema:
            coverage |= coverable_parts(schema["items"], schema_keys + ["items"])

    elif type_ in PRIMITIVE_TYPES_CLASSES:
        coverage.add("/".join(schema_keys))
        # TODO cover minimum, maximum, pattern, etc.

        if "enum" in schema:
            coverage.add("/".join(schema_keys + ["enum"]))

    else:
        raise ValueError(f"{type_} is not supported")

    return coverage


def cover_schema(schema, data, schema_keys=None):
    """Cover the schema with the data."""
    schema_keys = schema_keys or []
    type_ = schema.get("type", "object")

    coverage = set()

    if type_ in PRIMITIVE_TYPES_CLASSES:
        if type(data) == PRIMITIVE_TYPES_CLASSES[type_]:
            coverage.add(("/".join(schema_keys)))

    elif type_ == "object":
        if "properties" in schema:
            for k in schema["properties"]:
                if k in data:
                    coverage |= cover_schema(schema["properties"][k], data[k], schema_keys + [k])

        if "oneOf" in schema:
            for i, s in enumerate(schema["oneOf"]):
                try:
                    coverage |= cover_schema(s, data, schema_keys + [i])
                except ValueError:
                    pass

        if "additionalProperties" in schema:
            for k in data:
                if k not in schema.get("properties", {}):
                    coverage |= cover_schema(schema["additionalProperties"], data[k], schema_keys + [k])

    elif type_ == "array":
        if "items" in schema:
            for i, d in enumerate(data):
                coverage |= cover_schema(schema["items"], d, schema_keys + [i])

    else:
        # TODO cover minimum, maximum, pattern, etc.

        if "enum" in schema:
            if data not in schema["enum"]:
                raise ValueError(f"{data} is not in {schema['enum']}")

    return coverage
