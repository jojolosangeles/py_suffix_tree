"""Location within a suffix tree."""
from suffix_tree.node import Node


class Location:
    ON_NODE = -1

    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node, data_store):
        self.data_store = data_store
        self.locate_on_node(node)

    def ending_node(self):
        if self.next_edge_offset == 0:
            return self.node
        else:
            return self.edge.adjacent_node

    def locate_on_node(self, node):
        self.node = node
        self.next_edge_offset = 0

    def locate_on_edge_start(self, value):
        self.edge = self.node.children[value]
        if self.edge.edge_length == 1:
            self.node = self.edge.adjacent_node
            self.next_edge_offset = 0
        else:
            self.next_edge_offset = 1
            self.value_key = value
        return True

    def locate_on_edge(self, node, offset):
        self.node = node
        self.data_offset = offset
        self.on_node = node.offset_is_on_node(offset)
        return True

    def next_edge_at(self, offset):
        return self.node.children[self.data_store.value_at(offset)]

    def next_data_offset(self):
        self.next_edge_offset += 1
        if self.next_edge_offset == self.edge.edge_length:
            self.node = self.edge.adjacent_node
            self.next_edge_offset = 0

    def follow_edge_value(self, value):
        result = self.data_store.value_at(self.edge.start_offset + self.next_edge_offset) == value
        if result:
            self.next_data_offset()
        return result

    def follow_value(self, value):
        """Follow a value to a new location.

        Returns:
            True if the value was followed and Location changed
            False otherwise
        """
        if self.next_edge_offset > 0:
            return self.follow_edge_value(value)
        elif self.node.has_child_value(value):
            return self.locate_on_edge_start(value)
        else:
            return False

    def go_to_suffix(self):
        """
        Traverse to the suffix for this node.

        Return:
                True if the location changed
                False otherwise
        """
        if self.node.is_root():
            return False

        if self.node.suffix_link is None:
            parent_suffix_node, value_offset, amount_to_traverse = self.node.get_suffix_traversal_info()
            self.skip_count_down(parent_suffix_node, value_offset, amount_to_traverse)
            return True
        else:
            self.locate_on_node(self.node.suffix_link)
            return True

    def skip_count_down(self, node, offset, amount_to_traverse):
        """Traverse down a node starting at a given offset in the data
        source when the path down is assumed to exist (skip/count), so
        we only check first value when traversing edge down.
        """
        self.locate_on_node(node)
        if amount_to_traverse > 0:
            edge = self.next_edge_at(offset)
            if edge.covers(amount_to_traverse):
                self.next_edge_offset = amount_to_traverse
                self.edge = edge
            else:
                amount_to_traverse -= edge.edge_length
                self.skip_count_down(edge.adjacent_node, offset + edge.edge_length, amount_to_traverse)

    def __repr__(self):
        return "node({}), incoming {}-{}, data_offset {}, on_node={}".\
                format(self.node.id,
                       self.node.incoming_edge_start_offset,
                       self.node.incoming_edge_end_offset,
                       self.data_offset, self.on_node)


