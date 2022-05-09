[
    {
        precedence: 0.0,
        target: `speed`,
        operator: StatementOperators.SET,
        operand: {
            operator: ExpressionOperators.ADD,
            operands: [
                {
                    operator: ExpressionOperators.MULTIPLY,
                    operands: [
                        {
                            operator: ExpressionOperators.DYNAMIC_VALUE,
                            operands: `baseSpeedModifier`
                        },
                        {
                            operator: ExpressionOperators.MAX,
                            operands: [
                                {
                                    operator: ExpressionOperators.STATIC_VALUE,
                                    operands: 1
                                },
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
                                                            operands: `attributes.dexterity.value`
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
                                }
                            ]
                        }
                    ]
                },
                {
                    operator: ExpressionOperators.STATIC_VALUE,
                    operands: 15
                }
            ]
        }
    }
]