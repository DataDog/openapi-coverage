from openapi_coverage import cover_schema, coverable_parts, build_url_map


def test_cover_schema_primitive_types():
    schema = {"type": "string"}
    result = list(cover_schema(schema, "test"))
    assert result[0] == tuple()
    result = list(cover_schema(schema, 1))
    assert result == []

    schema = {"type": "integer"}
    result = list(cover_schema(schema, 1))
    assert result[0] == tuple()
    result = list(cover_schema(schema, "1"))
    assert result == []

    schema = {"type": "number"}
    result = list(cover_schema(schema, 1.0))
    assert result[0] == tuple()
    result = list(cover_schema(schema, "1.0"))
    assert result == []

    schema = {"type": "boolean"}
    result = list(cover_schema(schema, True))
    assert result[0] == tuple()
    result = list(cover_schema(schema, "True"))
    assert result == []


def test_coverable_parts():
    schema = {
        "type": "object",
        "properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
    }
    result = coverable_parts(schema)
    assert result == {("a",), ("b",)}


def test_schemas(load_yaml, load_json, dereference):
    schema = dereference(load_yaml("schemas/allOf.yaml"))
    dog = load_json("data/allOf/valid/dog.json")

    result = cover_schema(schema["components"]["schemas"]["Dog"], dog)
    assert result == {("allOf", 0, "pet_type"), ("allOf", 1, "bark")}


def test_url_map(load_yaml, dereference):
    schema = dereference(load_yaml("schemas/petstore.yaml"))
    url_map = build_url_map(schema)
    map_adapter = url_map.bind("http://localhost:8080")

    assert map_adapter.match("/pets", "GET") == (("paths", "/pets", "get"), {})
    assert map_adapter.match("/pets", "POST") == (("paths", "/pets", "post"), {})
    assert map_adapter.match("/pets/42", "GET") == (("paths", "/pets/{petId}", "get"), {"petId": "42"})
