from suffix_tree.node import Node


class TreeLocation:
    """A location within a suffix tree, either on a node or on an edge,
    as well as a specific location within the sequence of values used to create
    the suffix tree."""
    def __init__(self, node):
        self.node = node
        self.data_source_value_offset = Node.UNDEFINED_OFFSET
        self.node_needing_suffix_link = None

    @property
    def data_source_value_offset(self):
        return self._data_source_value_offset

    @data_source_value_offset.setter
    def data_source_value_offset(self, data_source_value_offset):
        self.on_node = (self.node.incoming_edge_end_offset == data_source_value_offset)
        self._data_source_value_offset = data_source_value_offset

    def update_node_needing_suffix_link(self, new_node):
        if self.node_needing_suffix_link != None:
            self.node_needing_suffix_link.suffix_link = new_node
        self.node_needing_suffix_link = new_node

    def set_suffix_link(self):
        if self.node_needing_suffix_link != None and self.on_node:
            self.node_needing_suffix_link.suffix_link = self.node
            self.node_needing_suffix_link = None

    def __repr__(self):
        if self.on_node:
            return "location: {!r}".format(self.node)
        else:
            return "location: {!r}[{}]".format(self.node, self.data_source_value_offset)

