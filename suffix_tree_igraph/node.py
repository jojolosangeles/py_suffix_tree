"""Node within a suffix tree."""
from suffix_tree_igraph.igraph_adapter import igraph_is_root, igraph_is_leaf, igraph_get_incoming_edge_length


class Node:
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""

    def __init__(self, id):
        self.id = id

    def is_root(self):
        return igraph_is_root(self.id)

    def is_leaf(self):
        return igraph_is_leaf(self.id)

    def incoming_edge_length(self):
        return igraph_get_incoming_edge_length(self.id)


class RootNode(Node):
    def __init__(self, id):
        super().__init__(id)

    def incoming_edge_length(self):
        return 0


class LeafNode(Node):
    def __init__(self, id):
        super().__init__(id)

    def incoming_edge_length(self):
        return 0
