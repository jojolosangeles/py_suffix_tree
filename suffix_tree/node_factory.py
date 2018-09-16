from suffix_tree.node import RootNode, LeafNode, Node
from itertools import count


class NodeFactory:
    def __init__(self, suffix_linker):
        self.suffix_generator = (i for i in count())
        self.id_generator = (i for i in count())
        self.suffix_linker = suffix_linker

    def final_id(self):
        return next(self.id_generator)

    def create_leaf(self, node, value, offset):
        leaf = LeafNode(next(self.id_generator), offset, next(self.suffix_generator))
        self.add_child(node, value, leaf)
        return leaf

    def create_internal(self, value, node, value2, end_offset):
        new_node = Node(next(self.id_generator), node.incoming_edge_start_offset, end_offset, { value2: node }, None)
        node.incoming_edge_start_offset = end_offset + 1
        self.add_child(node.parent, value, new_node)
        node.parent = new_node
        self.suffix_linker.needs_suffix_link(new_node)
        return new_node

    def create_root(self):
        return RootNode(next(self.id_generator))

    def add_child(self, parent, value, child):
        parent.children[value] = child
        child.parent = parent

