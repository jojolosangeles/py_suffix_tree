"""Location within a suffix tree."""


class Location:
    NO_DATA_OFFSET = -1

    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node_id, data_offset = NO_DATA_OFFSET, start_offset = NO_DATA_OFFSET, end_offset = NO_DATA_OFFSET):
        self.node_id = node_id
        self.end_offset = end_offset
        self.start_offset = start_offset
        self.data_offset = data_offset
        self.on_node = (data_offset == self.NO_DATA_OFFSET) or (end_offset != self.NO_DATA_OFFSET and data_offset == end_offset)

    def incoming_edge_length(self):
        return self.end_offset - self.start_offset + 1

    def __repr__(self):
        return "node({}), incoming ends at {}, data_offset {}, on_node={}".\
                format(self.node_id,
                       self.end_offset,
                       self.data_offset, self.on_node)


class LocationFactory:
    @classmethod
    def create_on_node(cls, location, node_id, start_offset, end_offset):
        location.node_id = node_id
        location.data_offset = end_offset
        location.start_offset = start_offset
        location.end_offset = end_offset
        location.on_node = True
        return location

    @classmethod
    def create_at_offset(cls, location, node_id, offset, start_offset, end_offset):
        location.node_id = node_id
        location.data_offset = offset
        location.start_offset = start_offset
        location.end_offset = end_offset
        location.on_node = end_offset == offset
        return location

    @classmethod
    def next_data_offset(cls, location):
        location.data_offset += 1
        location.on_node = location.end_offset == location.data_offset
        return location
