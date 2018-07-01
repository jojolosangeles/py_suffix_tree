
class Location:
    ON_INCOMING_EDGE_START = -1
    ON_NODE = -2

    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node, data_offset):
        self.node = node
        if data_offset == Location.ON_INCOMING_EDGE_START:
            data_offset = node.incoming_edge_start_offset
        elif data_offset == Location.ON_NODE:
            data_offset = node.incoming_edge_end_offset
        self.data_offset = data_offset
        self.on_node = (self.node.incoming_edge_end_offset == data_offset)

    def __repr__(self):
        if self.on_node:
            return "location: {!r}".format(self.node)
        else:
            return "location: {!r}[{}]".format(self.node, self.data_offset)


class LocationFactory:
    @classmethod
    def create(cls, node, offset = Location.ON_NODE):
        return Location(node, offset)

    @classmethod
    def next_data_offset(cls, location):
        return Location(location.node, location.data_offset + 1)
