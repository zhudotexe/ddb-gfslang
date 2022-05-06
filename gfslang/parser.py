import os

import lark
from lark import Lark, Transformer, v_args

from .imf_ast import (
    BinOp,
    Call,
    Feature,
    FunctionalMacroDef,
    FunctionalMacroSig,
    Literal,
    Macro,
    MacroCall,
    MacroDef,
    Statement,
    Target,
    Ternary,
)


# ===== transformer, parser -> IMF ast =====
# noinspection PyMethodMayBeStatic
@v_args(inline=True, meta=True)
class GFSTransformer(Transformer):
    @v_args(inline=False, meta=True)
    def feature(self, meta: lark.tree.Meta, children):
        return Feature(children).populate_posinfo(meta)

    # ==== macros ====
    def static_macro_def(self, meta: lark.tree.Meta, identifier, expression):
        return MacroDef(str(identifier), expression).populate_posinfo(meta)

    def functional_macro_def(self, meta: lark.tree.Meta, signature, expression):
        return FunctionalMacroDef(signature, expression).populate_posinfo(meta)

    def fmacro_sig(self, meta: lark.tree.Meta, identifier, *arg_names: str):
        return FunctionalMacroSig(str(identifier), *arg_names).populate_posinfo(meta)

    def fmacro_arg(self, _, identifier):
        return str(identifier)

    def ternary(self, meta: lark.tree.Meta, condition, true, false):
        return Ternary(condition, true, false).populate_posinfo(meta)

    # ==== GFS statements ====
    def rule_statement(self, meta: lark.tree.Meta, precedence, target, statement_op, expression):
        return Statement(float(precedence), str(target), str(statement_op), expression).populate_posinfo(meta)

    def a_num(self, meta: lark.tree.Meta, left, op, right):
        return BinOp(left, str(op), right).populate_posinfo(meta)

    def m_num(self, meta: lark.tree.Meta, left, op, right):
        return BinOp(left, str(op), right).populate_posinfo(meta)

    def call(self, meta: lark.tree.Meta, identifier, *args):
        return Call(str(identifier), *args).populate_posinfo(meta)

    def literal(self, meta: lark.tree.Meta, number: lark.Token):
        try:
            return Literal(int(number)).populate_posinfo(meta)
        except ValueError:
            return Literal(float(number)).populate_posinfo(meta)

    def target(self, meta: lark.tree.Meta, target: lark.Token):
        return Target(target.value).populate_posinfo(meta)

    def macro(self, meta: lark.tree.Meta, identifier: lark.Token):
        return Macro(identifier.value).populate_posinfo(meta)

    def macro_call(self, meta: lark.tree.Meta, identifier: lark.Token, *args):
        return MacroCall(identifier.value, *args).populate_posinfo(meta)


with open(os.path.join(os.path.dirname(__file__), "gfs.lark")) as f:
    grammar = f.read()
parser = Lark(grammar, start="feature", propagate_positions=True)
transformer = GFSTransformer()


def parse(feature: str) -> Feature:
    parsed = parser.parse(feature)
    return transformer.transform(parsed)


if __name__ == "__main__":
    while True:
        result = parser.parse(input())
        print(result.pretty())
        expr = transformer.transform(result)
        print(repr(expr))

# 0.5: attributes.${statName}.modifier = (attributes.${statName}.value - 10) // 2
#
# <Feature statements=[
#     <Statement
#     precedence=0.5
#     target='attributes.${statName}.modifier'
#     op='='
#     expression=<BinOp
#         left=<BinOp
#             left=<Target attributes.${statName}.value>
#             op='-'
#             right=<Literal 10>>
#         op='//'
#         right=<Literal 2>>
#     >
# ]>
