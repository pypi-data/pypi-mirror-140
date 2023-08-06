from .Block import Block
from .Children import Children
from .btype import FILE, DIR

def make_children(*child) -> Children:
    return Children.make(child)