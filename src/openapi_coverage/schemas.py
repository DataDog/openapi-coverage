"""Calculate coverage for schemas."""

from __future__ import nested_scopes
from .refs import get_ref

PRIMITIVE_TYPES_CLASSES = {
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "string": str,
}


def coverable_parts(schema, schema_keys=None, refs=None):
    """Return schema parts that should be tested."""
    coverage = set()

    # avoid infinite recursion
    if refs is not None:
        ref = get_ref(schema)
        if ref is not None:
            if ref in refs:
                return coverage
            refs.add(ref)

    schema_keys = schema_keys or []
    type_ = schema.get("type", "object")

    if type_ == "object":
        if schema_keys:
            coverage.add(tuple(schema_keys))
        if "properties" in schema:
            for k in schema["properties"]:
                coverage |= coverable_parts(
                    schema["properties"][k],
                    schema_keys=schema_keys + ["properties", k],
                    refs=refs,
                )

        if "oneOf" in schema:
            for i, s in enumerate(schema["oneOf"]):
                coverage |= coverable_parts(
                    s,
                    schema_keys=schema_keys + ["oneOf", i],
                    refs=refs,
                )

        if "allOf" in schema:
            for i, s in enumerate(schema["allOf"]):
                coverage |= coverable_parts(
                    s,
                    schema_keys=schema_keys + ["allOf", i],
                    refs=refs,
                )

        if "additionalProperties" in schema:
            nested_schema = schema["additionalProperties"]
            if schema["additionalProperties"] is True:
                nested_schema = {}
            elif schema["additionalProperties"] is False:
                nested_schema = None

            if nested_schema is not None:
                coverage |= coverable_parts(
                    nested_schema,
                    schema_keys=schema_keys + ["additionalProperties"],
                    refs=refs,
                )

    elif type_ == "array":
        if "items" in schema:
            coverage |= coverable_parts(
                schema["items"],
                schema_keys=schema_keys + ["items"],
                refs=refs,
            )

    elif type_ in PRIMITIVE_TYPES_CLASSES:
        coverage.add(tuple(schema_keys))
        # TODO cover minimum, maximum, pattern, etc.

        if "enum" in schema:
            for index in range(len(schema["enum"])):
                coverage |= {tuple(schema_keys + ["enum", index])}

    else:
        raise ValueError(f"{type_} is not supported")

    return coverage


def cover_schema(schema, data, schema_keys=None):
    """Cover the schema with the data."""
    schema_keys = schema_keys or []
    type_ = schema.get("type", "object")

    coverage = set()

    if type_ in PRIMITIVE_TYPES_CLASSES:
        if isinstance(data, PRIMITIVE_TYPES_CLASSES[type_]):
            coverage.add(tuple(schema_keys))
        if "enum" in schema:
            if data not in schema["enum"]:
                raise ValueError(f"{data} is not in {schema['enum']}")
            coverage.add(tuple(schema_keys + ["enum", schema["enum"].index(data)]))

    elif type_ == "object":
        if schema_keys:
            coverage.add(tuple(schema_keys))
        if "properties" in schema:
            for k in schema["properties"]:
                if data and k in data:
                    coverage |= cover_schema(
                        schema["properties"][k],
                        data[k],
                        schema_keys + ["properties", k],
                    )

        if "oneOf" in schema:
            for i, s in enumerate(schema["oneOf"]):
                try:
                    coverage |= cover_schema(s, data, schema_keys + ["oneOf", i])
                except (ValueError, TypeError):
                    pass

        if "allOf" in schema:
            for i, s in enumerate(schema["allOf"]):
                coverage |= cover_schema(s, data, schema_keys + ["allOf", i])

        if "additionalProperties" in schema:
            if schema["additionalProperties"] is not False and data is not None:
                additionalPropertiesSchema = schema["additionalProperties"]
                if isinstance(additionalPropertiesSchema, bool) and additionalPropertiesSchema == True:
                    additionalPropertiesSchema = {}

                for k in data:
                    if k not in schema.get("properties", {}):
                        coverage |= cover_schema(
                            additionalPropertiesSchema,
                            data[k],
                            schema_keys + ["additionalProperties"],
                        )

    elif type_ == "array":
        if "items" in schema:
            if data:
                for i, d in enumerate(data):
                    coverage |= cover_schema(schema["items"], d, schema_keys + ["items"])

    return coverage
