from suffix_tree.node import RootNode, LeafNode, Node

class NodeFactory:
    """Create basic nodes"""
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
    """Create nodes with ids"""
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

