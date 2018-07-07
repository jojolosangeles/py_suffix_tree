"""Node within a suffix tree."""


class Node:
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""
    def __init__(self, id, incoming_edge_start_offset, incoming_edge_end_offset, children, suffix_link=None):
        self.node_id = id
        self.incoming_edge_start_offset = incoming_edge_start_offset
        self.incoming_edge_end_offset = incoming_edge_end_offset
        self.children = children
        self.suffix_link = suffix_link

    def is_root(self):
        return self.incoming_edge_start_offset == Node.UNDEFINED_OFFSET and \
               self.incoming_edge_end_offset == Node.UNDEFINED_OFFSET and \
               self.suffix_link == self

    def is_internal(self):
        return self.incoming_edge_start_offset >= 0 and \
               self.incoming_edge_end_offset >= 0 and \
               len(self.children) > 0

    def is_leaf(self):
        return len(self.children) == 0 and \
               self.incoming_edge_start_offset >= 0 and \
               self.incoming_edge_end_offset == Node.UNDEFINED_OFFSET

    @property
    def incoming_edge_length(self):
        if self.is_leaf() or self.is_root():
            return 0
        return self.incoming_edge_end_offset - self.incoming_edge_start_offset + 1

class RootNode(Node):
    def __init__(self, id):
        super().__init__(id, Node.UNDEFINED_OFFSET, Node.UNDEFINED_OFFSET, {}, self)


class LeafNode(Node):
    def __init__(self, id, incoming_edge_start_offset, suffix_offset):
        super().__init__(id, incoming_edge_start_offset, Node.UNDEFINED_OFFSET, {})
        self.suffix_offset = suffix_offset

