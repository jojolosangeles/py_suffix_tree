from suffix_tree.node import RootNode, LeafNode, InternalNode, Edge, edge_save, Node
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
            # bad assumption, location.edge is "owned" by a node, can be passed around
            # creating problem for changing edge to be singleton, edge_copy() creates copy if necessary
            leaf_parent = self._split_edge(location.node, location._target_node, location._target_start_offset, location.edge_copy(), location.next_edge_offset)
            location.node = leaf_parent
            location.next_edge_offset = 0
        return self._create_leaf(location.node, value, offset)

    def _create_leaf(self, node, value, offset):
        new_leaf = LeafNode(next(self.id_generator), next(self.suffix_generator))
        Node.save_parent(new_leaf.id, node.id)
        node.children[value] = Edge(offset, -1, new_leaf)
        node.children_ids[value] = new_leaf.id
        return node

    def _split_edge(self, parent_node, target_node, target_start_offset, original_edge, next_edge_offset):
        # modify the original_edge
        new_internal_node = InternalNode(next(self.id_generator), {})
        Node.save_parent(new_internal_node.id, parent_node.id)
        Node.save_parent(target_node.id, new_internal_node.id)
        new_internal_parent_edge = Edge(target_start_offset, next_edge_offset, new_internal_node)
        original_edge.shrink_by(next_edge_offset)
        parent_node.children[self.data_store.value_at(target_start_offset)] = new_internal_parent_edge
        parent_node.children_ids[self.data_store.value_at(target_start_offset)] = new_internal_parent_edge.adjacent_node.id
        new_internal_node.children[self.data_store.value_at(original_edge.start_offset)] = original_edge
        new_internal_node.children_ids[self.data_store.value_at(original_edge.start_offset)] = original_edge.adjacent_node.id

        # same thing, but now update flat structures
        edge_save(original_edge.adjacent_node.id, original_edge.start_offset, original_edge.edge_length)
        return new_internal_node

    def create_root(self):
        return RootNode(next(self.id_generator))


