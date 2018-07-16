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

    def locate_on_node(self, node):
        self.node = node
        self.data_offset = node.incoming_edge_end_offset
        self.start_offset = node.incoming_edge_start_offset
        self.end_offset = node.incoming_edge_end_offset
        self.on_node = True

    def locate_on_edge(self, node, offset):
        self.node = node
        self.data_offset = offset
        self.start_offset = node.incoming_edge_start_offset
        self.end_offset = node.incoming_edge_end_offset
        self.on_node = self.end_offset == offset

    def next_data_offset(self):
        self.data_offset += 1
        self.on_node = self.end_offset == self.data_offset

    def __repr__(self):
        return "node({}), incoming {}-{}, data_offset {}, on_node={}".\
                format(self.node.id,
                       self.node.incoming_edge_start_offset,
                       self.node.incoming_edge_end_offset,
                       self.data_offset, self.on_node)


