from openapi_coverage import cover_schema, coverable_parts

def test_cover_schema_primitive_types():
    schema={
        "type": "string"
    }
    result = list(cover_schema(schema, "test"))
    assert result[0] == ""
    result = list(cover_schema(schema, 1))
    assert result == []

    schema={
        "type": "integer"
    }
    result = list(cover_schema(schema, 1))
    assert result[0] == ""
    result = list(cover_schema(schema, "1"))
    assert result == []

    schema={
        "type": "number"
    }
    result = list(cover_schema(schema, 1.0))
    assert result[0] == ""
    result = list(cover_schema(schema, "1.0"))
    assert result == []

    schema={
        "type": "boolean"
    }
    result = list(cover_schema(schema, True))
    assert result[0] == ""
    result = list(cover_schema(schema, "True"))
    assert result == []


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
