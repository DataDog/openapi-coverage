"""Load YAML file."""

from yaml.constructor import Constructor
from yaml.nodes import ScalarNode
from yaml.resolver import BaseResolver
from yaml import Loader


class PositionLoader(Loader):
    """Load YAML file."""

    def compose_node(self, parent, index):
        line = self.line
        column = self.column
        node = super().compose_node(parent, index)
        node.__position__ = {"line": line, "column": column}
        return node

    def construct_mapping(self, node, deep=False):
        node_pair_lst = node.value
        node_pair_lst_for_appending = []

        for key_node, value_node in node_pair_lst:
            shadow_key_node = ScalarNode(
                tag=BaseResolver.DEFAULT_SCALAR_TAG,
                value="__position__" + key_node.value,
            )
            shadow_value_node = ScalarNode(
                tag=BaseResolver.DEFAULT_SCALAR_TAG,
                value={
                    "line": key_node.__position__["line"] + 1,
                    "column": key_node.__position__["column"],
                },
            )
            node_pair_lst_for_appending.append((shadow_key_node, shadow_value_node))

        node.value = node_pair_lst + node_pair_lst_for_appending
        mapping = Constructor.construct_mapping(self, node, deep=deep)
        return mapping

    def construct_sequence(self, node, deep=False):
        values = []
        for value in node.value:
            values.append(value)
            position = value.__position__.copy()
            position["line"] += 1
            values.append(
                ScalarNode(
                    tag=BaseResolver.DEFAULT_SCALAR_TAG, value=position
                )
            )
        node.value = values
        return Constructor.construct_sequence(self, node, deep=deep)
