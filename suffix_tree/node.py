"""Node within a suffix tree."""


class Node:
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""

    def __init__(self, id, incoming_edge_start_offset, incoming_edge_end_offset=UNDEFINED_OFFSET, children=None,
                 suffix_link=None):
        self.id = id
        self.incoming_edge_start_offset = incoming_edge_start_offset
        self.incoming_edge_end_offset = incoming_edge_end_offset
        self.children = children
        self.suffix_link = suffix_link

    def is_root(self):
        return self.suffix_link == self

    def is_leaf(self):
        return self.children is None

    def incoming_edge_length(self):
        return self.incoming_edge_end_offset - self.incoming_edge_start_offset + 1


class RootNode(Node):
    def __init__(self, id):
        super().__init__(id, Node.UNDEFINED_OFFSET, Node.UNDEFINED_OFFSET, {}, self)

    def incoming_edge_length(self):
        return 0


class LeafNode(Node):
    def __init__(self, id, incoming_edge_start_offset, suffix_offset):
        super().__init__(id, incoming_edge_start_offset)
        self.suffix_offset = suffix_offset

    def incoming_edge_length(self):
        return 0
