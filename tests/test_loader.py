from pathlib import Path

from openapi_coverage.loader import PositionLoader


def test_position():
    with Path(__file__).parent.joinpath("schemas/petstore.yaml").open() as f:
        schema = PositionLoader(f.read()).get_single_data()

    assert schema["components"]["schemas"]["Pet"]["__position__properties"]["line"] == 89
