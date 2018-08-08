from suffix_tree.node import RootNode, InternalNode, edge_save, Node, edge_adjust
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
            leaf_parent = self._split_edge(location.node, location._target_node,
                                           location._target_start_offset, location.next_edge_offset)
            location.node = leaf_parent
            location.next_edge_offset = 0
        return self._create_leaf(location.node, value, offset)

    def _create_leaf(self, node, value, offset):
        new_leaf_id = next(self.id_generator)
        new_suffix_offset =  next(self.suffix_generator)
        Node.save_new_leaf_info(new_leaf_id, node.id, new_suffix_offset)
        node.children_ids[value] = new_leaf_id
        edge_save(new_leaf_id, offset, -1)
        return node

    def _split_edge(self, parent_node, target_node, target_start_offset, next_edge_offset):
        new_internal_node = InternalNode(next(self.id_generator))
        Node.save_parent(new_internal_node.id, parent_node.id)
        Node.save_parent(target_node.id, new_internal_node.id)
        edge_adjust(target_node.id, next_edge_offset)
        parent_node.children_ids[self.data_store.value_at(target_start_offset)] = new_internal_node.id
        new_internal_node.children_ids[self.data_store.value_at(Node.incoming_edge_start_offset(target_node.id))] = target_node.id
        edge_save(new_internal_node.id, target_start_offset, next_edge_offset)
        return new_internal_node

    def create_root(self):
        return RootNode(next(self.id_generator))


