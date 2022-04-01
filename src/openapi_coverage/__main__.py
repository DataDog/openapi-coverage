import sys

import yaml
from jsonref import JsonRef
from yaml import CSafeLoader

from .har import cover_har, load_har
from .paths import build_url_map, coverable_paths
from .refs import replace_refs
from .trie import build_trie

schema_path = sys.argv[1]

with open(schema_path) as f:
    schema = JsonRef.replace_refs(yaml.load(f, Loader=CSafeLoader))

coverred = set()
url_map = build_url_map(schema)

for har_path in sys.argv[2:]:
    har = load_har(har_path)
    coverred |= cover_har(schema, har, url_map=url_map)

coverable = coverable_paths(schema)
coverable_trie = build_trie(coverable)
coverred_trie = build_trie(coverred)

# for c in sorted({replace_refs(schema, c) for c in coverred}):
#     print(c)

for operation in sorted({p[:3] for p in coverable}):
    c = coverred_trie.count_children(operation)
    ca = coverable_trie.count_children(operation)
    if c > 0:
        r = 100.0 * c / ca
    else:
        r = 0
    print(f"{r:>6.2f}% - {operation[1:]}")

total_coverage = 100.0 * len(coverred)/len(coverable)
print(f"Total coverage: {total_coverage:.2f}%")
