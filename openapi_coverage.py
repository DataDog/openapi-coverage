"""Generage OpenAPI coverage."""


def cover_schema(schema, data, schema_keys=None):
    """Cover the schema with the data."""
    schema_keys = schema_keys or []
    type_ = schema.get("type", "object")

    if type_ == "object":
        if "properties" in schema:
            for k in schema["properties"]:
                if k in data:
                    cover_schema(schema["properties"][k], data[k], schema_keys + [k])
                    
        if "oneOf" in schema:
            for i, s in enumerate(schema["oneOf"]):
                try:
                    cover_schema(s, data, schema_keys + [i])
                except ValueError:
                    pass

        if "additionalProperties" in schema:
            for k in data:
                if k not in schema.get("properties", {}):
                    cover_schema(schema["additionalProperties"], data[k], schema_keys + [k])
                    
    elif type_ == "array":
        if "items" in schema:
            for i, d in enumerate(data):
                cover_schema(schema["items"], d, schema_keys + [i])
    
    else:
        # TODO cover minimum, maximum, pattern, etc.
        
        if "enum" in schema:
            if data not in schema["enum"]:
                raise ValueError(f"{data} is not in {schema['enum']}")
