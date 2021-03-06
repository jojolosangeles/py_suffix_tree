"""Node within a suffix tree."""


class Node:
    """Node represents a sub-sequence of values found at multiple locations in the total sequence.
    The exact locations in the total sequence are in the LeafNodes 'suffix_offset' values below
    this Node.  A LeafNode respresents only one location (the suffix_offset), and a RootNode
    represents all locations."""
    UNDEFINED_OFFSET = -1
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


class NodeFlattener:
    def __init__(self, writer):
        self.writer = writer

    def write_root(self, node):
        self.writer.write("{id}\n".format(id=node.id))

    def write_leaf(self, node):
        self.writer.write("{id} {parent_id} {incoming_sequence_id} {suffix_offset}\n".format(
            id = node.id,
            parent_id = node.parent.id,
            incoming_sequence_id = node.incoming_sequence_id,
            suffix_offset = node.suffix_offset
        ))

    def write_internal(self, node):
        self.writer.write("{id} {parent_id} {incoming_sequence_id}\n".format(
            id = node.id,
            parent_id = node.parent.id,
            incoming_sequence_id = node.incoming_sequence_id
        ))