from openapi_coverage import cover_schema, coverable_parts

def test_cover_schema():
    schema={
        "type": "string"
    }
    result = list(cover_schema(schema, "test"))
    assert result[0] == tuple(("", True))


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
    result = list(coverable_parts(schema))
    assert result == ["/a", "/b"]