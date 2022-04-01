import json
from pathlib import Path

import pytest
import yaml
from jsonref import JsonRef
from yaml import CSafeLoader


@pytest.fixture(scope="session")
def load_yaml():
    def loader(path):
        with (Path(__file__).parent / path).open("r") as f:
            return yaml.load(f, Loader=CSafeLoader)

    return loader


@pytest.fixture(scope="session")
def load_json():
    def loader(path):
        with (Path(__file__).parent / path).open("r") as f:
            return json.load(f)

    return loader


@pytest.fixture(scope="session")
def dereference():
    def loader(schema):
        return JsonRef.replace_refs(schema)

    return loader
