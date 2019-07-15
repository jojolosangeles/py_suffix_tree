from suffix_tree.node import GraphNode
from itertools import count

class NodeFactory:
    """NodeFactory is used by the Ukkonen algorithm implementation to create Node instances
    as a sequence of values is processed."""
    def __init__(self, suffix_linker):
        self.suffixOffsetGenerator = (i for i in count())
        self.id_generator = (i for i in count())
        self.suffix_linker = suffix_linker

    def nextInternalId(self):
        return next(self.id_generator)

    def final_suffix(self):
        return next(self.suffixOffsetGenerator)

    def create_root(self):
        return GraphNode.create_root()

    def create_leaf(self, node, value, offset):
        leaf = GraphNode.create_leaf(node.PK, value, offset, next(self.suffixOffsetGenerator))
        leaf.parent = node
        return leaf

    def create_internal(self, incomingEdgeValueSequence):
        return GraphNode.create_internal(f"i{self.nextInternalId()}", incomingEdgeValueSequence)

    def add_child(self, parent, value, child):
        parent.children[value] = child
        child.parent = parent

