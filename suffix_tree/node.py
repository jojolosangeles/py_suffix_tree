
class Node:
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""
    def __init__(self, incoming_edge_start_offset, incoming_edge_end_offset, children, suffix_link=None):
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
        return self.incoming_edge_end_offset - self.incoming_edge_start_offset + 1


class RootNode(Node):
    def __init__(self):
        super().__init__(Node.UNDEFINED_OFFSET, Node.UNDEFINED_OFFSET, {}, self)


class LeafNode(Node):
    def __init__(self, incoming_edge_start_offset, suffix_offset):
        super().__init__(incoming_edge_start_offset, Node.UNDEFINED_OFFSET, {})
        self.suffix_offset = suffix_offset

class NodeFactory:
    def __init__(self):
        self.suffix_offset = 0

    def create_leaf(self, node, value, offset):
        leaf = LeafNode(offset, self.suffix_offset)
        self.suffix_offset += 1
        self.add_child(node, value, leaf)
        return leaf

    def create_internal(self, value, node, value2, end_offset):
        new_node = Node(node.incoming_edge_start_offset, end_offset, {}, None)
        node.incoming_edge_start_offset = end_offset + 1
        self.add_child(node.parent, value, new_node)
        self.add_child(new_node, value2, node)
        return new_node

    def create_root(self):
        return RootNode()

    def add_child(self, parent, value, child):
        parent.children[value] = child
        child.parent = parent

class NodeFactoryWithId(NodeFactory):
    def __init__(self):
        super().__init__()
        self.node_id = 0

    def next_node_id(self):
        result = self.node_id
        self.node_id += 1
        return result

    def create_leaf(self, node, value, offset):
        leaf = super().create_leaf(node, value, offset)
        leaf.node_id = self.next_node_id()

    def create_internal(self, value, node, value2, end_offset):
        new_node = super().create_internal(value, node, value2, end_offset)
        new_node.node_id = self.next_node_id()
        return new_node

    def create_root(self):
        result = super().create_root()
        result.node_id = self.next_node_id()
        return result

