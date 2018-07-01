from suffix_tree.node import Node

class Location:
    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node, offset = Node.UNDEFINED_OFFSET):
        self.node = node
        self.data_offset = offset

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, new_node):
        self._node = new_node
        self.on_node = True

    @property
    def data_offset(self):
        return self._data_source_value_offset

    @data_offset.setter
    def data_offset(self, data_source_value_offset):
        self.on_node = (self.node.incoming_edge_end_offset == data_source_value_offset)
        self._data_source_value_offset = data_source_value_offset

    def __repr__(self):
        if self.on_node:
            return "location: {!r}".format(self.node)
        else:
            return "location: {!r}[{}]".format(self.node, self.data_offset)

