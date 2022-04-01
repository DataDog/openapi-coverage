from openapi_coverage.trie import build_trie

def test_build_trie():
    coverage = set()
    coverage.add(("a", "b", "c", "e", "f"))
    coverage.add(("a", "g", "h"))

    t = build_trie(coverage)

    assert t.count_children(("a")) == 6
    assert t.count_children(("a", "b")) == 3
    assert t.count_children(("a", "g")) == 1
    assert t.count_children(("a", "g", "h")) == 0


