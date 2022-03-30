from openapi_coverage import cover_schema, coverable_parts

def test_cover_schema_primitive_types():
    schema={
        "type": "string"
    }
    result = list(cover_schema(schema, "test"))
    assert result[0] == tuple(("", True))
    result = list(cover_schema(schema, 1))
    assert result[0] == tuple(("", False))

    schema={
        "type": "integer"
    }
    result = list(cover_schema(schema, 1))
    assert result[0] == tuple(("", True))
    result = list(cover_schema(schema, "1"))
    assert result[0] == tuple(("", False))

    schema={
        "type": "number"
    }
    result = list(cover_schema(schema, 1.0))
    assert result[0] == tuple(("", True))
    result = list(cover_schema(schema, "1.0"))
    assert result[0] == tuple(("", False))

    schema={
        "type": "boolean"
    }
    result = list(cover_schema(schema, True))
    assert result[0] == tuple(("", True))
    result = list(cover_schema(schema, "True"))
    assert result[0] == tuple(("", False))


def test_coverable_parts():
    schema={
        "type": "object",
        "properties": {
            "a": {
                "type": "string"
            },
            "b": {
                "type": "integer"
            }
        }
    }
    result = coverable_parts(schema)
    assert result == {"a", "b"}
