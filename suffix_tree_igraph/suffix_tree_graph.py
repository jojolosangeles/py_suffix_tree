from itertools import count
from suffix_tree_igraph.suffix_linker import SuffixLinker


class SuffixTreeGraph:
    def __init__(self, strategy):
        self.strategy = strategy
        self.root = self.strategy.create_root()
        self.strategy.add_suffix_link(self.root, self.root)
        self.suffix_generator = (i for i in count())
        self.suffix_linker = SuffixLinker(self.strategy.add_suffix_link)

    def is_root(self, node):
        return node == self.root

    def is_leaf(self, node):
        so, eo = self.get_incoming_edge_offsets(node)
        return so > eo

    def get_parent(self, node):
        return self.strategy.get_parent(node)

    def get_incoming_edge_offsets(self, node):
        return self.strategy.get_incoming_edge_offsets(node)

    def get_suffix_link(self, node):
        return self.strategy.get_suffix_link(node)

    def get_suffix_offset(self, leaf):
        return self.strategy.get_suffix_offset(leaf)

    def has_outgoing_edge(self, node, key):
        return self.strategy.has_outgoing_edge(node, key)

    def create_leaf(self, parent, value, offset):
        return self.strategy.create_leaf(next(self.suffix_generator), parent, value, offset)

    def create_internal(self, parent_key, node, new_node_child_key, new_node_end_offset):
        incoming_edge_start_offset, incoming_edge_end_offset = self.strategy.get_incoming_edge_offsets(node)
        parent = self.strategy.get_parent(node)
        new_node = self.strategy.split_edge(
            parent, parent_key, incoming_edge_start_offset, new_node_end_offset,
            node, new_node_child_key, new_node_end_offset + 1, incoming_edge_end_offset)
        self.suffix_linker.needs_suffix_link(new_node)
        return new_node