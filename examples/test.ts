[
    {
        precedence: 0.5,
        target: `attributes.strength.modifier`,
        operator: StatementOperators.SET,
        operand: {
            operator: ExpressionOperators.MAX,
            operands: [
                {
                    operator: ExpressionOperators.FLOOR,
                    operands: [
                        {
                            operator: ExpressionOperators.MULTIPLY,
                            operands: [
                                {
                                    operator: ExpressionOperators.ADD,
                                    operands: [
                                        {
                                            operator: ExpressionOperators.DYNAMIC_VALUE,
                                            operands: `attributes.strength.value`
                                        },
                                        {
                                            operator: ExpressionOperators.STATIC_VALUE,
                                            operands: -10
                                        }
                                    ]
                                },
                                {
                                    operator: ExpressionOperators.STATIC_VALUE,
                                    operands: 0.5
                                }
                            ]
                        }
                    ]
                },
                {
                    operator: ExpressionOperators.STATIC_VALUE,
                    operands: -5
                }
            ]
        }
    }
]