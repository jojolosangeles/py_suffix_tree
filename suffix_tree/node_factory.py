from suffix_tree.node import RootNode, LeafNode, InternalNode, Edge, edge_save
from itertools import count


class NodeFactory:
    def __init__(self, data_store):
        self.suffix_generator = (i for i in count())
        self.id_generator = (i for i in count())
        self.data_store = data_store

    def final_id(self):
        return next(self.id_generator)

    def create_leaf(self, location, value, offset):
        if location.next_edge_offset > 0:
            leaf_parent = self._split_edge(location.node, location.edge, location.next_edge_offset)
            location.node = leaf_parent
            location.next_edge_offset = 0
        return self._create_leaf(location.node, value, offset)

    def _create_leaf(self, node, value, offset):
        new_leaf = LeafNode(next(self.id_generator), node, None, next(self.suffix_generator))
        node.children[value] = new_leaf.parent_edge = Edge(offset, -1, new_leaf)
        node.children_ids[value] = new_leaf.id
        return node

    def _split_edge(self, node, original_edge, next_edge_offset):
        # modify the original_edge
        new_internal_node = InternalNode(next(self.id_generator), node.id, original_edge, {})
        original_start_offset = original_edge.start_offset
        new_internal_parent_edge = Edge(original_start_offset, next_edge_offset, new_internal_node)
        new_internal_node.parent_edge = new_internal_parent_edge
        original_edge.start_offset += next_edge_offset
        original_edge.edge_length -= next_edge_offset
        node.children[self.data_store.value_at(original_start_offset)] = new_internal_parent_edge
        node.children_ids[self.data_store.value_at(original_start_offset)] = new_internal_parent_edge.adjacent_node.id
        new_internal_node.children[self.data_store.value_at(original_edge.start_offset)] = original_edge
        original_edge.adjacent_node.parent = new_internal_node
        new_internal_node.parent = node

        # same thing, but now update flat structures
        edge_save(original_edge.adjacent_node.id, original_edge.start_offset, original_edge.edge_length)
        return new_internal_node

    def create_root(self):
        return RootNode(next(self.id_generator))


