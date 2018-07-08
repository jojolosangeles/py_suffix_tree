"""Location within a suffix tree."""


class Location:
    ON_NODE = -1

    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node, data_offset):
        self.node = node
        if data_offset == Location.ON_NODE:
            data_offset = node.incoming_edge_end_offset
        self.data_offset = data_offset
        self.on_node = (self.node.incoming_edge_end_offset == data_offset)

    def __repr__(self):
        return "node({}), incoming {}-{}, data_offset {}, on_node={}".\
                format(self.node.node_id,
                       self.node.incoming_edge_start_offset,
                       self.node.incoming_edge_end_offset,
                       self.data_offset, self.on_node)


class LocationFactory:
    @classmethod
    def createOnNode(cls, location, node):
        location.node = node
        location.data_offset = location.node.incoming_edge_end_offset
        location.on_node = True
        return location

    @classmethod
    def create(cls, location, node, offset):
        location.node = node
        location.data_offset = offset
        location.on_node = location.node.incoming_edge_end_offset == offset
        return location #Location(node, offset)

    @classmethod
    def next_data_offset(cls, location):
        return Location(location.node, location.data_offset + 1)
