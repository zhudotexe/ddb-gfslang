# ddb-gfs-dsl

This repo contains a proof-of-concept DSL/parser/compiler to make writing GFS statements fast!

## Usage

```bash
$ python gfsc.py gfs_file_here.gfs [-o output_file_name.ts]
```

If an output file name is not provided, the filename will be `(name of input file).ts`.

## Installation

GFSLang is built in Python using the Lark parsing library and requires Python 3.10+. I recommend using a virtual
environment to keep your dependencies contained to the GFSLang project:

Unix:

```bash
$ python --version
Python 3.10.0
$ python -m venv venv
$ source venv/bin/activate
```

Windows:

```bash
$ python --version
Python 3.10.0
$ python -m venv venv
$ venv\Scripts\activate.bat
```

Then, install the dependencies using `pip`:

```bash
(venv) $ pip install -r requirements.txt
```

## Example

Why write this:

```
{
    precedence: 0.5,
    target: `attributes.${statName}.modifier`,
    operator: StatementOperators.SET,
    operand: {
        operator: ExpressionOperators.FLOOR,
        operands: [
            {
                operator: ExpressionOperators.MULTIPLY,
                operands: [
                    {
                        operator: ExpressionOperators.STATIC_VALUE,
                        operands: 0.5,
                    },
                    {
                        operator: ExpressionOperators.ADD,
                        operands: [
                            { operator: ExpressionOperators.STATIC_VALUE, operands: -10 },
                            {
                                operator: ExpressionOperators.DYNAMIC_VALUE,
                                operands: `attributes.${statName}.value`,
                            },
                        ],
                    },
                ],
            },
        ],
    },
},
```

When you can write this?

```
0.5: attributes.${statName}.modifier = (attributes.${statName}.value - 10) // 2
```

Look in `examples/` for more examples!

## Grammar

A single GFSLang program is called a "feature," stored in a single `.gfs` file. Each feature is comprised of a list
of statements.

A statement can either be a final rule, or a compiler macro definition:

### Macros

**Static Macro**

```
(name) := (expression)
```

This saves an expression to the temporary name *name*, allowing it to be used elsewhere in rule definitions.
Macro names must be valid identifiers (only contain letters, numbers, and underscore, must not start with a number).

**Functional Macro**

```
NAME(arg, arg, arg...) := FMACRO_EXPRESSION
```

This creates a functional macro that can be called inside an expression, lazily evaluating the right hand side of the
definition at call-time. The expressions passed to a functional macro will be bound as macros themselves with the
argument name for the evaluation of the right hand side.

Functional macros support recursion and JS-like ternary statements (using static expressions only) on their right hand
side.

The macro name and argument names must be valid identifiers.

### Rules

```
(precendence): (target) [=|++] (expression)
```

where:

- precedence is a number
- target is an arbitrary string
- the operator `=` is used for assignment, and the operator `++` is used for pushing to a list

**Expression**

An expression can be any of the following:

- an arithmetic statement (e.g. `5 + 2`, `attributes.${statName}.value - 10`); supported operations:
    - addition
    - subtraction
    - multiplication
    - division
    - floor division (`//`)
- a call to a function like `min` or `floor` (e.g. `min(0.5, -10)`); supported functions:
    - `max(a[, b, c...])`
    - `min(a[, b, c...])`
    - `floor(x)`
- a literal number (e.g. `0.5`, `-10`)
- a target name (e.g. `attributes.${statName}.value`)
- a macro (e.g. `!halfStrengthMod`)

### Comments

Any text following a hash (e.g. `# this is a comment`) is considered a comment and has no semantic meaning in GFSL.

## Order of Operations

GFSL follows PEMDAS where applicable.

1. GFSLang (string) -> intermediate AST (gfslang.imf_ast) via `gfslang.parse`
2. intermediate AST -> GFS AST (gfslang.gfs_ast) via `gfslang.compile`
3. GFS AST -> TypeScript/JSON via `gfslang.render`
