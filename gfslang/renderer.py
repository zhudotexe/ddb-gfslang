"""
The renderer is responsible for taking a GFS AST and outputting a TypeScript program or JSON.
"""
import abc
import numbers
import textwrap
from typing import List

from . import gfs_ast


class Renderer(abc.ABC):
    def render(self, feature: List[gfs_ast.Statement]) -> str:
        raise NotImplementedError


class TSRenderer(Renderer):
    """Outputs the GFSL program as a TypeScript object."""

    def render(self, feature: List[gfs_ast.Statement]) -> str:
        statements = []
        for stmt in feature:
            stmt_inner = self.render_statement(stmt)
            statements.append(stmt_inner)
        return self.render_list(statements)

    @staticmethod
    def render_list(elems: List[str]) -> str:
        inner = textwrap.indent(",\n".join(elems), " " * 4)
        return f"[\n{inner}\n]"

    def render_statement(self, stmt: gfs_ast.Statement) -> str:
        operand_inner = textwrap.indent(self.render_expression(stmt.operand), " " * 4).strip()
        return (
            textwrap.dedent(
                """
                {{
                    precedence: {precedence},
                    target: `{target}`,
                    operator: StatementOperators.{operator},
                    operand: {operand}
                }}
                """
            )
            .strip()
            .format(precedence=stmt.precedence, target=stmt.target, operator=stmt.operator.value, operand=operand_inner)
        )

    def render_expression(self, expr: gfs_ast.Expression) -> str:
        if isinstance(expr.operands, (int, float)):
            operands_inner = str(expr.operands)
        elif isinstance(expr.operands, str):
            operands_inner = f"`{expr.operands}`"
        else:
            operand_inners = [self.render_expression(operand) for operand in expr.operands]
            operands_inner = textwrap.indent(self.render_list(operand_inners), " " * 4).strip()
        return (
            textwrap.dedent(
                """
                {{
                    operator: ExpressionOperators.{operator},
                    operands: {operands}
                }}
                """
            )
            .strip()
            .format(operator=expr.operator.value, operands=operands_inner)
        )
