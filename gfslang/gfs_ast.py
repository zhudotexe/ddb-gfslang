"""
GFS AST: This is an abstract representation of the final data structure that gets sent to the GFS engine.
It is the final output of the compiler.

See https://github.com/DnDBeyond/ddb-characters/blob/devgr/rpn-calc/packages/gfs/src/types.ts.
"""
import enum
from typing import List, Union


class ExpressionOperators(enum.Enum):
    ADD = "ADD"
    MIN = "MIN"
    MAX = "MAX"
    FLOOR = "FLOOR"
    MULTIPLY = "MULTIPLY"
    DYNAMIC_VALUE = "DYNAMIC_VALUE"
    STATIC_VALUE = "STATIC_VALUE"


class StatementOperators(enum.Enum):
    SET = "SET"
    PUSH = "PUSH"


class Expression:
    def __init__(self, operator: ExpressionOperators, operands: Union[List["Expression"], str, int, float]):
        self.operator = operator
        self.operands = operands


class StaticExpression(Expression):
    """Compiler optimization: this expression is always static"""

    __match_args__ = ("operands",)

    def __init__(self, operand: Union[int, float]):
        super().__init__(ExpressionOperators.STATIC_VALUE, operand)


class Statement:
    def __init__(self, precedence: float, target: str, operator: StatementOperators, operand: Expression):
        self.precedence = precedence
        self.target = target
        self.operator = operator
        self.operand = operand
