from suffix_tree.node import Node

class TreeLocation:
    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node):
        self.node = node
        self.data_source_value_offset = Node.UNDEFINED_OFFSET

    @property
    def data_source_value_offset(self):
        return self._data_source_value_offset

    @data_source_value_offset.setter
    def data_source_value_offset(self, data_source_value_offset):
        self.on_node = (self.node.incoming_edge_end_offset == data_source_value_offset)
        self._data_source_value_offset = data_source_value_offset

    def __repr__(self):
        if self.on_node:
            return "location: {!r}".format(self.node)
        else:
            return "location: {!r}[{}]".format(self.node, self.data_source_value_offset)

