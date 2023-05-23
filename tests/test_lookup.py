from pathlib import Path

from openapi_coverage.loader import PositionLoader
from openapi_coverage.lookup import lookup, lookup_endline


def test_lookup():
    with Path(__file__).parent.joinpath("schemas/petstore.yaml").open() as f:
        schema = PositionLoader(f.read()).get_single_data()

    assert lookup(schema, ("components", "schemas", "Pet", "__position__properties"))["line"] == 89


def test_lookup_endline():
    with Path(__file__).parent.joinpath("schemas/petstore.yaml").open() as f:
        schema = PositionLoader(f.read()).get_single_data()

    assert lookup_endline(schema, ("components", "schemas", "Pet", "properties")) == 96


def test_list_lookup_endline():
    with Path(__file__).parent.joinpath("schemas/petstore.yaml").open() as f:
        schema = PositionLoader(f.read()).get_single_data()

    assert lookup_endline(schema, ("paths", "/pets", "get", "parameters", 0, "schema")) == 23


def test_last_lookup_endline():
    with Path(__file__).parent.joinpath("schemas/petstore.yaml").open() as f:
        schema = PositionLoader(f.read()).get_single_data()

    assert lookup_endline(schema, ("components", "schemas", "Error", "properties"), 111) == 111


def test_last_section_lookup_endline():
    with Path(__file__).parent.joinpath("schemas/petstore.yaml").open() as f:
        schema = PositionLoader(f.read()).get_single_data()

    assert lookup_endline(schema, ("paths", "/pets/{petId}", "get", "responses")) == 81
