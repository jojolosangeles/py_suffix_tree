"""Location within a suffix tree."""
from suffix_tree_igraph.igraph_adapter import igraph_get_incoming_edge_end_offset, igraph_get_incoming_edge_offsets


class Location:
    ON_NODE = -1

    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node, data_offset):
        self.node = node
        incoming_edge_end_offset = igraph_get_incoming_edge_end_offset(node.id)
        if data_offset == Location.ON_NODE:
            data_offset = incoming_edge_end_offset
        self.data_offset = data_offset
        self.on_node = (incoming_edge_end_offset == data_offset)

    def __repr__(self):
        incoming_edge_start_offset, incoming_edge_end_offset = igraph_get_incoming_edge_offsets(self.node.id)
        return "node({}), incoming {}-{}, data_offset {}, on_node={}".\
                format(self.node.id,
                       incoming_edge_start_offset,
                       incoming_edge_end_offset,
                       self.data_offset, self.on_node)


class LocationFactory:
    @classmethod
    def createOnNode(cls, location, node):
        location.node = node
        location.data_offset = igraph_get_incoming_edge_end_offset(node.id)
        location.on_node = True
        return location

    @classmethod
    def create(cls, location, node, offset):
        location.node = node
        location.data_offset = offset
        location.on_node = igraph_get_incoming_edge_end_offset(node.id) == offset
        return location

    @classmethod
    def next_data_offset(cls, location):
        return Location(location.node, location.data_offset + 1)
