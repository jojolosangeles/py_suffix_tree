"""Node within a suffix tree."""

class Edge:
    def __init__(self, start_offset, edge_length, adjacent_node):
        self.start_offset = start_offset
        self.edge_length = edge_length
        self.adjacent_node = adjacent_node

    def covers(self, length):
        return self.edge_length > length or self.edge_length < 0

class Node:
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""

    def __init__(self, id):
        self.id = id

    def is_root(self):
        return False

    def is_leaf(self):
        return False

    def is_internal(self):
        return True

class NodeWithChildren(Node):
    def __init__(self, id, children):
        super().__init__(id)
        self.children = children

    def has_child_value(self, value):
        return value in self.children

class InternalNode(NodeWithChildren):
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""

    def __init__(self, id, parent_edge, children):
        super().__init__(id, children)
        self.parent_edge = parent_edge
        self.suffix_link = None

    def get_suffix_traversal_info(self):
        parent = self.parent
        value_offset = self.parent_edge.start_offset
        amount_to_traverse = self.parent_edge.edge_length
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
        super().__init__(id, {})
        self.suffix_link = self

    def is_root(self):
        return True


class LeafNode(Node):
    def __init__(self, id, parent, parent_edge, suffix_offset):
        super().__init__(id)
        self.parent = parent
        self.parent_edge = parent_edge
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