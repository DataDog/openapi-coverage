from openapi_coverage import cover_schema

def test_cover_schema():
    schema={
        "type": "string"
    }
    result = cover_schema(schema, "test")
    assert list(result)[0] == tuple(("", True))
