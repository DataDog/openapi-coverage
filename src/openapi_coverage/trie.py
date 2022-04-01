from typing import Dict, Set, List


class TrieNode:
    def __init__(self, value: str, children: Dict):
        self.value = value
        self.children = children or dict()


class Trie:
    def __init__(self):
        self.root = TrieNode("root", None)

    def insert(self, path):
        current = self.root
        for k in path:
            if k not in current.children:
                current.children[k] = TrieNode(k, None)
            current = current.children[k]

    def get(self, path):
        current = self.root
        for k in path:
            if k not in current.children:
                return None
            current = current.children[k]
        return current

    def count_children(self, path):
        root = self.get(path)

        if not root:
            return -1

        cnt = 0
        q = [root]

        # BFS
        while q:
            cur = q[0]
            q.pop(0)

            cnt += len(cur.children)

            for k, v in cur.children.items():
                q.append(v)

        return cnt


def build_trie(coverage: List) -> Trie:
    trie = Trie()
    for path in coverage:
        trie.insert(path)
    return trie
