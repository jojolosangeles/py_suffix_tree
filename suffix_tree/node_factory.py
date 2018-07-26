from suffix_tree.node import RootNode, LeafNode, InternalNode, Edge
from itertools import count


class NodeFactory:
    def __init__(self, data_store):
        self.suffix_generator = (i for i in count())
        self.id_generator = (i for i in count())
        self.data_store = data_store

    def final_id(self):
        return next(self.id_generator)

    def create_leaf(self, location, value, offset):
        leaf_parent = location.node
        if location.next_edge_offset > 0:
            leaf_parent = self._split_edge(location.node,
                                                 location.value_key,
                                                 location.edge,
                                                 location.next_edge_offset)
        self._create_leaf(leaf_parent, value, offset)
        location.node = leaf_parent
        location.next_edge_offset = 0
        return leaf_parent

    def _create_leaf(self, node, value, offset):
        new_leaf = LeafNode(next(self.id_generator), node, None, next(self.suffix_generator))
        new_edge = Edge(offset, -1, new_leaf)
        new_leaf.parent_edge = new_edge
        node.children[value] = new_edge

    def _split_edge(self, node, value_key, original_edge, next_edge_offset):
        leaf_parent_edge = Edge(original_edge.start_offset + next_edge_offset, original_edge.edge_length - next_edge_offset, original_edge.adjacent_node)
        original_edge.adjacent_node.parent_edge = leaf_parent_edge
        new_internal_node = InternalNode(next(self.id_generator), original_edge, { self.data_store.value_at(leaf_parent_edge.start_offset): leaf_parent_edge })
        original_edge.edge_length = next_edge_offset
        original_edge.adjacent_node.parent = new_internal_node
        original_edge.adjacent_node = new_internal_node
        new_internal_node.parent = node
        return new_internal_node

    def create_root(self):
        return RootNode(next(self.id_generator))


