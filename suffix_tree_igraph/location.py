"""Location within a suffix tree."""
from suffix_tree_igraph.igraph_adapter import igraph_get_incoming_edge_end_offset, igraph_get_incoming_edge_offsets


class Location:
    ON_NODE = -1

    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node_id, data_offset):
        self.node_id = node_id
        incoming_edge_end_offset = igraph_get_incoming_edge_end_offset(self.node_id)
        if data_offset == Location.ON_NODE:
            data_offset = incoming_edge_end_offset
        self.data_offset = data_offset
        self.on_node = (incoming_edge_end_offset == data_offset)

    def __repr__(self):
        incoming_edge_start_offset, incoming_edge_end_offset = igraph_get_incoming_edge_offsets(self.node_id)
        return "node({}), incoming {}-{}, data_offset {}, on_node={}".\
                format(self.node_id,
                       incoming_edge_start_offset,
                       incoming_edge_end_offset,
                       self.data_offset, self.on_node)


class LocationFactory:
    @classmethod
    def create_on_node(cls, location, node_id):
        location.node_id = node_id
        location.data_offset = igraph_get_incoming_edge_end_offset(node_id)
        location.on_node = True
        return location

    @classmethod
    def create(cls, location, node_id, offset):
        location.node_id = node_id
        location.data_offset = offset
        location.on_node = igraph_get_incoming_edge_end_offset(node_id) == offset
        return location

    @classmethod
    def next_data_offset(cls, location):
        return Location(location.node_id, location.data_offset + 1)
