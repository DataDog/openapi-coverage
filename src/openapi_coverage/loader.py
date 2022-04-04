"""Load YAML file."""

import ruamel
from ruamel.yaml import YAML


class Str(ruamel.yaml.scalarstring.ScalarString):
    __slots__ = "lc"

    style = ""

    def __new__(cls, value):
        return ruamel.yaml.scalarstring.ScalarString.__new__(cls, value)


class MyPreservedScalarString(ruamel.yaml.scalarstring.PreservedScalarString):
    __slots__ = "lc"


class MyDoubleQuotedScalarString(ruamel.yaml.scalarstring.DoubleQuotedScalarString):
    __slots__ = "lc"


class MySingleQuotedScalarString(ruamel.yaml.scalarstring.SingleQuotedScalarString):
    __slots__ = "lc"


class LCBoolean(ruamel.yaml.scalarbool.ScalarBoolean):
    lc = None


class LCInt(ruamel.yaml.scalarint.ScalarInt):
    lc = None


class LCFloat(ruamel.yaml.scalarfloat.ScalarFloat):
    lc = None


class LCConstructor(ruamel.yaml.constructor.RoundTripConstructor):
    def construct_scalar(self, node):
        # type: (Any) -> Any
        if not isinstance(node, ruamel.yaml.nodes.ScalarNode):
            raise ruamel.yaml.constructor.ConstructorError(
                None,
                None,
                "expected a scalar node, but found %s" % node.id,
                node.start_mark,
            )

        if node.style == "|" and isinstance(node.value, ruamel.yaml.compat.text_type):
            ret_val = MyPreservedScalarString(node.value)
        elif bool(self._preserve_quotes) and isinstance(
            node.value, ruamel.yaml.compat.text_type
        ):
            if node.style == "'":
                ret_val = MySingleQuotedScalarString(node.value)
            elif node.style == '"':
                ret_val = MyDoubleQuotedScalarString(node.value)
            else:
                ret_val = Str(node.value)
        else:
            ret_val = Str(node.value)
        ret_val.lc = ruamel.yaml.comments.LineCol()
        ret_val.lc.line = node.start_mark.line
        ret_val.lc.col = node.start_mark.column
        return ret_val

    def construct_yaml_float(self, node):
        # type: (Any) -> Any
        b = super(LCConstructor, self).construct_yaml_float(node)
        if node.anchor:
            ret_val = LCFloat(b, anchor=node.anchor)
        else:
            ret_val = LCFloat(b)
        ret_val.lc = ruamel.yaml.comments.LineCol()
        ret_val.lc.line = node.start_mark.line
        ret_val.lc.col = node.start_mark.column
        return ret_val

    # def construct_yaml_seq(self, node):

    # def construct_yaml_map(self, node):

    def construct_yaml_int(self, node):
        # type: (Any) -> Any
        b = super(LCConstructor, self).construct_yaml_int(node)
        if node.anchor:
            ret_val = LCInt(b, anchor=node.anchor)
        else:
            ret_val = LCInt(b)
        ret_val.lc = ruamel.yaml.comments.LineCol()
        ret_val.lc.line = node.start_mark.line
        ret_val.lc.col = node.start_mark.column
        return ret_val

    def construct_yaml_bool(self, node):
        # type: (Any) -> Any
        b = super(LCConstructor, self).construct_yaml_bool(node)
        import ipdb; ipdb.set_trace()
        if node.anchor:
            ret_val = LCBoolean(b, anchor=node.anchor)
        else:
            ret_val = LCBoolean(b)
        ret_val.lc = ruamel.yaml.comments.LineCol()
        ret_val.lc.line = node.start_mark.line
        ret_val.lc.col = node.start_mark.column
        return ret_val


LCConstructor.add_constructor(
    'tag:yaml.org,2002:bool', LCConstructor.construct_yaml_bool
)

LCConstructor.add_constructor(
    'tag:yaml.org,2002:int', LCConstructor.construct_yaml_int
)

LCConstructor.add_constructor(
    'tag:yaml.org,2002:float', LCConstructor.construct_yaml_float
)


yaml = YAML()
yaml.Constructor = LCConstructor
