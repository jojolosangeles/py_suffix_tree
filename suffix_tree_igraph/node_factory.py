from itertools import count

from suffix_tree_igraph.igraph_adapter import igraph_add_edge, igraph_remove_edge, igraph_add_vertex, igraph_parent_id, \
    igraph_add_suffix_link, igraph_get_incoming_edge_offsets, igraph_add_leaf


class NodeFactory:
    def __init__(self, suffix_linker):
        self.suffix_generator = (i for i in count())
        self.id_generator = (i for i in count())
        self.suffix_linker = suffix_linker

    def final_id(self):
        return next(self.id_generator)

    def create_leaf(self, parent_node_id, value, offset):
        leaf_id = next(self.id_generator)
        igraph_add_leaf(next(self.suffix_generator))
        igraph_add_edge(parent_node_id, leaf_id, value, offset, -1)
        return leaf_id

    def create_internal(self, value, node_id, value2, end_offset):
        incoming_edge_start_offset, incoming_edge_end_offset = igraph_get_incoming_edge_offsets(node_id)
        new_node_id = next(self.id_generator)
        igraph_add_vertex()
        parent_id = igraph_parent_id(node_id)
        igraph_add_edge(parent_id, new_node_id, value, incoming_edge_start_offset, end_offset)
        igraph_add_edge(new_node_id, node_id, value2, end_offset + 1, incoming_edge_end_offset)
        igraph_remove_edge(parent_id, node_id)
        self.suffix_linker.needs_suffix_link(new_node_id)
        return new_node_id

    def create_root(self):
        root_id = next(self.id_generator)
        igraph_add_vertex()
        igraph_add_suffix_link(root_id, root_id)
        return root_id


