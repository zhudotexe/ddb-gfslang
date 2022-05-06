import argparse
import os
import sys

import gfslang

argparser = argparse.ArgumentParser(description="Compile a GFSLang file to a typescript object.")
argparser.add_argument("input_file")
argparser.add_argument("-o", help="The filename of the output file to write.", metavar="output_file")


def debug():
    """random zhu code to debug, ignore me"""
    from gfslang import compile
    from gfslang.parser import parser, transformer
    from gfslang.renderer import TSRenderer

    with open(sys.argv[-1]) as f:
        expr = f.read()
    result = parser.parse(expr)
    print(result.pretty())
    expr = transformer.transform(result)
    print(repr(expr))
    compiled = compile(expr)
    rendered = TSRenderer().render(compiled)
    print(rendered)


def main():
    args = argparser.parse_args()
    if args.o:
        output_filename = args.o
    else:
        base_filename, _ = os.path.splitext(args.input_file)
        output_filename = f"{base_filename}.ts"

    with open(args.input_file) as f:
        expr = f.read()

    ast = gfslang.parse(expr)
    expr = gfslang.compile(ast)
    result = gfslang.render_ts(expr)

    with open(output_filename, "w") as f:
        f.write(result)


if __name__ == "__main__":
    main()
