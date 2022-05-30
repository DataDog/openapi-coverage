from openapi_coverage.trie import build_trie


def test_build_trie():
    coverage = set()
    coverage.add(("a", "b", "c", "e", "f"))
    coverage.add(("a", "g", "h"))

    t = build_trie(coverage)

    assert t.count_leafs(("a")) == 2
    assert t.count_leafs(("a", "b")) == 1
    assert t.count_leafs(("a", "g")) == 1
    assert t.count_leafs(("a", "g", "h")) == 1
