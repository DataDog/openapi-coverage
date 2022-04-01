import sys

import yaml
from jsonref import JsonRef
from yaml import CSafeLoader

from .har import cover_har, load_har
from .paths import build_url_map
from .refs import replace_refs

schema_path = sys.argv[1]

with open(schema_path) as f:
    schema = JsonRef.replace_refs(yaml.load(f, Loader=CSafeLoader))

coverred = set()
url_map = build_url_map(schema)

for har_path in sys.argv[2:]:
    har = load_har(har_path)
    coverred |= cover_har(schema, har, url_map=url_map)

for c in sorted({replace_refs(schema, c) for c in coverred}):
    print(c)
