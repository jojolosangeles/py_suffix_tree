"""Location within a suffix tree."""
from suffix_tree.node import Node


class Location:
    ON_NODE = -1

    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node, data_store):
        self.node = node
        self.data_offset = Node.UNDEFINED_OFFSET
        self.on_node = True
        self.data_store = data_store

    def locate_on_node(self, node):
        self.node = node
        self.on_node = True

    def locate_on_edge_start(self, node):
        return self.locate_on_edge(node, node.incoming_edge_start_offset)

    def locate_on_edge(self, node, offset):
        self.node = node
        self.data_offset = offset
        self.on_node = node.offset_is_on_node(offset)
        return True

    def next_node_at(self, offset):
        return self.node.children[self.data_store.value_at(offset)]

    def next_data_offset(self):
        self.data_offset += 1
        self.on_node = self.node.offset_is_on_node(self.data_offset)

    def follow_edge_value(self, value):
        result = self.data_store.value_at(self.data_offset + 1) == value
        if result:
            self.next_data_offset()
        return result

    def follow_value(self, value):
        """Follow a value to a new location.

        Returns:
            True if the value was followed and Location changed
            False otherwise
        """
        if not self.on_node:
            return self.follow_edge_value(value)
        elif self.node.has_child_value(value):
            return self.locate_on_edge_start(self.node.children[value])
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
            child = self.next_node_at(offset)
            if child.incoming_edge_covers(amount_to_traverse):
                self.locate_on_edge(child, child.incoming_edge_start_offset + amount_to_traverse - 1)
            else:
                edge_length = child.incoming_edge_length()
                amount_to_traverse -= edge_length
                self.skip_count_down(child, offset + edge_length, amount_to_traverse)

    def __repr__(self):
        return "node({}), incoming {}-{}, data_offset {}, on_node={}".\
                format(self.node.id,
                       self.node.incoming_edge_start_offset,
                       self.node.incoming_edge_end_offset,
                       self.data_offset, self.on_node)


