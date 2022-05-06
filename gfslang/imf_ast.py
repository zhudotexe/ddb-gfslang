"""
Intermediate Form AST: this AST is a representation of GFSLang including compiler directives like macros.
The compiler turns this into the GFS AST.
"""

import abc
from typing import List, Union

import lark.tree


class Node(abc.ABC):
    line: int
    column: int
    end_line: int
    end_column: int

    def populate_posinfo(self, meta: lark.tree.Meta):
        self.line = meta.line
        self.column = meta.column
        self.end_line = meta.end_line
        self.end_column = meta.end_column
        return self

    def copy_pos(self, node: "Node"):
        self.line = node.line
        self.column = node.column
        self.end_line = node.end_line
        self.end_column = node.end_column
        return self


class Feature(Node):
    def __init__(self, statements: List[Union["MacroDef", "Statement"]]):
        self.statements = statements

    def __repr__(self):
        return f"<{type(self).__name__} statements={self.statements!r}>"


# ==== macros ====
class MacroDef(Node):
    def __init__(self, identifier: str, expression: "Expression"):
        self.identifier = identifier
        self.expression = expression

    def __repr__(self):
        return f"<{type(self).__name__} identifier={self.identifier!r} expression={self.expression!r}>"


class FunctionalMacroDef(MacroDef):
    def __init__(self, signature: "FunctionalMacroSig", expression: "Expression"):
        super().__init__(signature.identifier, expression)
        self.args = signature.args


class FunctionalMacroSig(Node):
    def __init__(self, identifier: str, *arg_names: str):
        self.identifier = identifier
        self.args = arg_names


class Ternary(Node):
    def __init__(
        self,
        condition: Union["Ternary", "Expression"],
        true: Union["Ternary", "Expression"],
        false: Union["Ternary", "Expression"],
    ):
        self.condition = condition
        self.true = true
        self.false = false


# ==== GFS statements ====
class Statement(Node):
    def __init__(self, precedence: float, target: str, op: str, expression: "Expression"):
        self.precedence = precedence
        self.target = target
        self.op = op
        self.expression = expression

    def __repr__(self):
        return (
            f"<{type(self).__name__} precedence={self.precedence!r} target={self.target!r} op={self.op!r} "
            f"expression={self.expression!r}>"
        )


class Expression(Node, abc.ABC):
    pass


class BinOp(Expression):
    def __init__(self, left: Expression, op: str, right: Expression):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"<{type(self).__name__} left={self.left!r} op={self.op!r} right={self.right!r}>"


class Call(Expression):
    def __init__(self, name: str, *args: Expression):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"<{type(self).__name__} name={self.name!r} args={self.args!r}>"


class Literal(Expression):
    def __init__(self, value: Union[int, float]):
        self.value = value

    def __repr__(self):
        return f"<{type(self).__name__} {self.value}>"


class Target(Expression):
    def __init__(self, target: str):
        self.target = target

    def __repr__(self):
        return f"<{type(self).__name__} {self.target}>"


class Macro(Expression):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"<{type(self).__name__} !{self.name}>"


class MacroCall(Expression):
    def __init__(self, name: str, *args: Expression):
        self.name = name
        self.args = args

    def __repr__(self):
        arg_str = ", ".join(repr(arg) for arg in self.args)
        return f"<{type(self).__name__} !{self.name}({arg_str})>"
