import contextlib
import math
import operator
from typing import Dict, List, TypeVar

from . import errors, gfs_ast, imf_ast

_ExprT = TypeVar("_ExprT", bound=imf_ast.Expression)


class Compiler:
    valid_calls = {
        "min": gfs_ast.ExpressionOperators.MIN,
        "max": gfs_ast.ExpressionOperators.MAX,
        "floor": gfs_ast.ExpressionOperators.FLOOR,
    }
    # static arithmetic optimizations
    arithmetic_operators = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "//": operator.floordiv,
    }
    arithmetic_calls = {
        "min": min,
        "max": max,
        "floor": math.floor,
    }

    def __init__(self):
        self.macros: Dict[str, gfs_ast.Expression] = {}
        self.func_macros: Dict[str, imf_ast.FunctionalMacroDef] = {}

        self.expr_handlers = {
            imf_ast.BinOp: self.compile_binop,
            imf_ast.Call: self.compile_call,
            imf_ast.Literal: self.compile_literal,
            imf_ast.Target: self.compile_target,
            imf_ast.Macro: self.compile_macro,
            imf_ast.MacroCall: self.compile_macro_call,
        }

    def compile(self, feature: imf_ast.Feature) -> List[gfs_ast.Statement]:
        out = []
        for stmt in feature.statements:
            if isinstance(stmt, imf_ast.FunctionalMacroDef):
                self.compile_fmacro_def(stmt)
            elif isinstance(stmt, imf_ast.MacroDef):
                self.compile_macro_def(stmt)
            else:
                out.append(self.compile_statement(stmt))
        return out

    def compile_fmacro_def(self, fmacro_def: imf_ast.FunctionalMacroDef):
        if not len(set(fmacro_def.args)) == len(fmacro_def.args):
            raise errors.GFSLCompileError(f"Functional macro argument names must be unique", node=fmacro_def)
        self.func_macros[fmacro_def.identifier] = fmacro_def

    def compile_macro_def(self, macro_def: imf_ast.MacroDef):
        self.macros[macro_def.identifier] = self.compile_expression(macro_def.expression)

    def compile_statement(self, stmt: imf_ast.Statement) -> gfs_ast.Statement:
        if stmt.op == "=":
            op = gfs_ast.StatementOperators.SET
        elif stmt.op == "++":
            op = gfs_ast.StatementOperators.PUSH
        else:
            raise errors.GFSLFatalCompileError(f"Unknown statement operator: {stmt.op!r}", node=stmt)
        expr = self.compile_expression(stmt.expression)
        return gfs_ast.Statement(precedence=stmt.precedence, target=stmt.target, operator=op, operand=expr)

    def compile_expression(self, expr: _ExprT) -> gfs_ast.Expression:
        handler = self.expr_handlers.get(type(expr))
        if handler is None:
            raise errors.GFSLFatalCompileError(
                f"No compilation step defined for IMF node of type {type(expr)}", node=expr
            )
        # noinspection PyArgumentList
        # pycharm does not like the type narrowing here
        return handler(expr)

    def compile_binop(self, binop: imf_ast.BinOp) -> gfs_ast.Expression:
        left = self.compile_expression(binop.left)
        right = self.compile_expression(binop.right)
        op = binop.op
        match left, op, right:
            # --- simple math: both sides are static, we just evaluate it here ---
            case (gfs_ast.StaticExpression(left), op, gfs_ast.StaticExpression(right)):
                return gfs_ast.StaticExpression(self.arithmetic_operators[op](left, right))
            # --- special cases ---
            case (left, "-", gfs_ast.StaticExpression(right)):
                # since subtraction is not implemented, compile "a - 1" to "a + (-1)" (literals only)
                right_unfurled = gfs_ast.StaticExpression(-right)
                return gfs_ast.Expression(
                    operator=gfs_ast.ExpressionOperators.ADD,
                    operands=[left, right_unfurled],
                )
            case (left, "-", right):
                # since subtraction is not implemented, compile "a - b" to "a + (b * -1)"
                negative_right = gfs_ast.Expression(
                    operator=gfs_ast.ExpressionOperators.MULTIPLY,
                    operands=[right, gfs_ast.StaticExpression(-1)],
                )
                return gfs_ast.Expression(
                    operator=gfs_ast.ExpressionOperators.ADD,
                    operands=[left, negative_right],
                )
            case (left, "/", gfs_ast.StaticExpression(right)):
                # since division is not implemented, compile "a / 2" to "a * eval(1/2)" (literals only)
                if right == 0:
                    raise errors.GFSLCompileError("Cannot divide by zero", node=binop)
                right_recip = gfs_ast.StaticExpression(1 / right)
                return gfs_ast.Expression(
                    operator=gfs_ast.ExpressionOperators.MULTIPLY,
                    operands=[left, right_recip],
                )
            case (left, "//", gfs_ast.StaticExpression(right)):
                # since floor division is not implemented, compile "a // 2" to "floor(a * eval(1/2))" (literals only)
                if right == 0:
                    raise errors.GFSLCompileError("Cannot divide by zero", node=binop)
                right_recip = gfs_ast.StaticExpression(1 / right)
                floor_arg = gfs_ast.Expression(
                    operator=gfs_ast.ExpressionOperators.MULTIPLY,
                    operands=[left, right_recip],
                )
                return gfs_ast.Expression(
                    operator=gfs_ast.ExpressionOperators.FLOOR,
                    operands=[floor_arg],
                )
            case (_, "/" | "//", _):
                # cannot divide by dynamic expression
                raise errors.GFSLCompileError("Dividing by a dynamic expression is not allowed in the GFS", node=binop)
            # --- compiler optimizations ---
            case (expr, "+" | "-", gfs_ast.StaticExpression(0)) | (gfs_ast.StaticExpression(0), "+", expr):
                # additive ops with 0 (identity)
                return expr
            case (_, "*", gfs_ast.StaticExpression(0)) | (gfs_ast.StaticExpression(0), "*" | "/" | "//", _):
                # multiplicative ops with 0
                return gfs_ast.StaticExpression(0)
            case (expr, "*" | "/" | "//", gfs_ast.StaticExpression(1)) | (gfs_ast.StaticExpression(1), "*", expr):
                # multiplicative ops with 1 (identity)
                return expr
            # --- GFS base ops ---
            case imf_ast.BinOp(left, "+", right):
                return gfs_ast.Expression(
                    operator=gfs_ast.ExpressionOperators.ADD,
                    operands=[self.compile_expression(left), self.compile_expression(right)],
                )
            case imf_ast.BinOp(left, "*", right):
                return gfs_ast.Expression(
                    operator=gfs_ast.ExpressionOperators.MULTIPLY,
                    operands=[self.compile_expression(left), self.compile_expression(right)],
                )
        raise errors.GFSLFatalCompileError(
            f"Unhandled binary operator pattern: {type(left).__name__} {op!r} {type(right).__name__}", node=binop
        )

    def compile_call(self, call: imf_ast.Call) -> gfs_ast.Expression:
        if call.name not in self.valid_calls:
            raise errors.GFSLCompileError(f"Function !{call.name} is not defined", node=call)
        args = [self.compile_expression(arg) for arg in call.args]
        # simple math: all args are static and we know how to evaluate the arithmetic function
        if all(isinstance(arg, gfs_ast.StaticExpression) for arg in args) and call.name in self.arithmetic_calls:
            return gfs_ast.StaticExpression(self.arithmetic_calls[call.name](*(arg.operands for arg in args)))
        return gfs_ast.Expression(operator=self.valid_calls[call.name], operands=args)

    @staticmethod
    def compile_literal(literal: imf_ast.Literal) -> gfs_ast.Expression:
        return gfs_ast.StaticExpression(literal.value)

    @staticmethod
    def compile_target(target: imf_ast.Target) -> gfs_ast.Expression:
        return gfs_ast.Expression(operator=gfs_ast.ExpressionOperators.DYNAMIC_VALUE, operands=target.target)

    def compile_macro(self, macro: imf_ast.Macro) -> gfs_ast.Expression:
        if macro.name in self.macros:
            return self.macros[macro.name]
        raise errors.GFSLCompileError(f"Macro !{macro.name} is not defined", node=macro)

    @contextlib.contextmanager
    def _bind_fmacro_namespace(
        self, fmacro: imf_ast.FunctionalMacroDef, args: List[gfs_ast.Expression], calling_node: imf_ast.MacroCall
    ):
        if len(args) != len(fmacro.args):
            raise errors.GFSLCompileError(
                f"Incorrect number of arguments passed to !{fmacro.identifier}(): expected {len(fmacro.args)}, "
                f"got {len(args)}",
                node=calling_node,
            )
        old_ns = self.macros.copy()
        for arg_name, arg in zip(fmacro.args, args):
            self.macros[arg_name] = arg
        try:
            yield
        finally:
            self.macros = old_ns

    def compile_macro_call(self, macro_call: imf_ast.MacroCall) -> gfs_ast.Expression:
        if macro_call.name not in self.func_macros:
            raise errors.GFSLCompileError(f"Macro !{macro_call.name}() is not defined", node=macro_call)
        fmacro = self.func_macros[macro_call.name]
        args = [self.compile_expression(arg) for arg in macro_call.args]
        # now, we bind the args to the macro's args and compile the macro
        with self._bind_fmacro_namespace(fmacro, args, calling_node=macro_call):
            return self.compile_expression(fmacro.expression)


def compile(feature: imf_ast.Feature) -> List[gfs_ast.Statement]:
    return Compiler().compile(feature)
