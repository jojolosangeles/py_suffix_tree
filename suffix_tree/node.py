"""Node within a suffix tree."""


class Node:
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""

    def __init__(self, id, incoming_edge_start_offset):
        self.id = id
        self.incoming_edge_start_offset = incoming_edge_start_offset

    def is_root(self):
        return False

    def is_leaf(self):
        return False

    def is_internal(self):
        return True

class NodeWithChildren(Node):
    def __init__(self, id, children, incoming_edge_start_offset):
        super().__init__(id, incoming_edge_start_offset)
        self.children = children

    def has_child_value(self, value):
        return value in self.children

class InternalNode(NodeWithChildren):
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""

    def __init__(self, id, incoming_edge_start_offset, incoming_edge_end_offset, children):
        super().__init__(id, children, incoming_edge_start_offset)
        self.incoming_edge_end_offset = incoming_edge_end_offset
        self.suffix_link = None

    def get_suffix_traversal_info(self):
        amount_to_traverse = self.incoming_edge_length()
        parent = self.parent
        value_offset = self.incoming_edge_start_offset
        if parent.is_root():
            amount_to_traverse -= 1
            value_offset += 1
        return parent.suffix_link, value_offset, amount_to_traverse

    def is_internal(self):
        return True

    def incoming_edge_covers(self, length):
        return self.incoming_edge_length() >= length

    def incoming_edge_length(self):
        return self.incoming_edge_end_offset - self.incoming_edge_start_offset + 1

    def offset_is_on_node(self, offset):
        return self.incoming_edge_end_offset == offset

class RootNode(NodeWithChildren):
    def __init__(self, id):
        super().__init__(id, {}, Node.UNDEFINED_OFFSET)
        self.suffix_link = self

    def is_root(self):
        return True


class LeafNode(Node):
    def __init__(self, parent, id, incoming_edge_start_offset, suffix_offset):
        super().__init__(id, incoming_edge_start_offset)
        self.parent = parent
        self.suffix_offset = suffix_offset

    def incoming_edge_covers(self, length):
        return True

    def incoming_edge_length(self):
        raise AssertionError

    def offset_is_on_node(self, offset):
        return False

    def is_leaf(self):
        return True

    def has_child_value(self, value):
        return False