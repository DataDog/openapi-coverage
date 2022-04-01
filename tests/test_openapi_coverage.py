from openapi_coverage.schemas import cover_schema, coverable_parts
from openapi_coverage.paths import build_url_map, coverable_paths
from openapi_coverage.refs import replace_refs


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
    assert result == {
        (
            "properties",
            "a",
        ),
        (
            "properties",
            "b",
        ),
    }


def test_cover_all():
    schema = {
        "type": "object",
        "properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
    }
    data = {"a": "hello", "b": 85}

    total = coverable_parts(schema)
    actual = cover_schema(schema, data)
    coverage_percentage = len(total & actual) / len(total)

    assert coverage_percentage == 1.0


def test_partial_cover():
    schema = {
        "type": "object",
        "properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
    }

    data = {"a": "hello", "b": "85"}

    total = coverable_parts(schema)
    actual = cover_schema(schema, data)
    coverage_percentage = len(total & actual) / len(total)

    assert coverage_percentage == 0.5


def test_schemas(load_yaml, load_json, dereference):
    schema = dereference(load_yaml("schemas/allOf.yaml"))
    dog = load_json("data/allOf/valid/dog.json")

    result = cover_schema(schema["components"]["schemas"]["Dog"], dog)
    assert result == {
        ("allOf", 0, "properties", "pet_type"),
        ("allOf", 1, "properties", "bark"),
    }


def test_url_map(load_yaml, dereference):
    schema = dereference(load_yaml("schemas/petstore.yaml"))
    url_map = build_url_map(schema)
    map_adapter = url_map.bind("http://localhost:8080")

    assert map_adapter.match("/pets", "GET") == (("paths", "/pets", "get"), {})
    assert map_adapter.match("/pets", "POST") == (("paths", "/pets", "post"), {})
    assert map_adapter.match("/pets/42", "GET") == (
        ("paths", "/pets/{petId}", "get"),
        {"petId": "42"},
    )


def test_replace_refs(load_yaml, dereference):
    schema = dereference(load_yaml("schemas/allOf.yaml"))
    dog = {
        "pet_type": "Dog",
        "bark": True,
        "breed": "Labrador",
    }

    result = {
        replace_refs(schema, c)
        for c in cover_schema(
            schema["components"]["schemas"]["Dog"],
            dog,
            schema_keys=["components", "schemas", "Dog"],
        )
    }
    assert result == {
        ("components", "schemas", "Dog", "allOf", 1, "properties", "bark"),
        ("components", "schemas", "Dog", "allOf", 1, "properties", "breed"),
        ("components", "schemas", "Pet", "properties", "pet_type"),  # from allOf $ref
    }

def test_coverable_paths(load_yaml, dereference):
    schema = dereference(load_yaml("schemas/petstore.yaml"))
    assert coverable_paths(schema) == {('limit',), ('petId',)}
