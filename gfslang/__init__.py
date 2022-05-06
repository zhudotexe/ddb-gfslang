from .parser import parse
from .compiler import compile
from .renderer import TSRenderer


def render_ts(feature) -> str:
    return TSRenderer().render(feature)
