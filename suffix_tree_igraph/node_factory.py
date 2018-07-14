from itertools import count

from suffix_tree_igraph.igraph_adapter import igraph_add_edge, igraph_remove_edge, igraph_add_vertex, igraph_parent_id
from suffix_tree_igraph.node import RootNode, LeafNode, Node


class NodeFactory:
    def __init__(self, suffix_linker):
        self.suffix_generator = (i for i in count())
        self.id_generator = (i for i in count())
        self.suffix_linker = suffix_linker
        self.nodes = []

    def get_node_by_id(self, id):
        return self.nodes[id]

    def add_node(self, node):
        self.nodes.append(node)

    def final_id(self):
        return next(self.id_generator)

    def create_leaf(self, node, value, offset):
        leaf = LeafNode(next(self.id_generator), offset, next(self.suffix_generator))
        igraph_add_vertex()
        self.add_node(leaf)
        igraph_add_edge(node.id, leaf.id, value, offset, -1)
        return leaf

    def create_internal(self, value, node, value2, end_offset):
        new_node = Node(next(self.id_generator), node.incoming_edge_start_offset, end_offset, None)
        igraph_add_vertex()
        self.add_node(new_node)
        parent_id = igraph_parent_id(node.id)
        igraph_add_edge(parent_id, new_node.id, value, node.incoming_edge_start_offset, end_offset)
        igraph_add_edge(new_node.id, node.id, value2, end_offset + 1, node.incoming_edge_end_offset)
        igraph_remove_edge(parent_id, node.id)
        node.incoming_edge_start_offset = end_offset + 1
        self.suffix_linker.needs_suffix_link(new_node)
        return new_node

    def create_root(self):
        root = RootNode(next(self.id_generator))
        igraph_add_vertex()
        self.add_node(root)
        return root


