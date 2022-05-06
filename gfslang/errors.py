class GFSLError(Exception):
    """Base error in GFSLang."""

    pass


class GFSLSyntaxError(GFSLError):
    """Invalid syntax somewhere."""

    pass


class GFSLCompileError(GFSLError):
    """Something happened during compilation."""

    def __init__(self, msg, node):
        super().__init__(msg)
        self.line = node.line
        self.column = node.column
        self.end_line = node.end_line
        self.end_column = node.end_column


class GFSLFatalCompileError(GFSLCompileError):
    """Something went wrong during compilation, and it's the compiler's fault."""

    pass
