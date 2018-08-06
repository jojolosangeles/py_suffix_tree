"""Location within a suffix tree."""
from suffix_tree.node import Edge, Node


class Location:

    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node, data_store):
        self.data_store = data_store
        self.locate_on_node(node)
        self.my_edge = Edge(0, 0, None)
        self.edge = None

    def nearest_node_down(self):
        if self.next_edge_offset == 0:
            return self.node
        else:
            return self._target_node

    def locate_on_node(self, node):
        self.node = node
        self.next_edge_offset = 0

    def edge_copy(self):
        return Edge(self._target_start_offset, self._target_edge_length, self._target_node)
        #if self.edge == None or self.edge == self.my_edge:
        #    return self.my_edge.copy()
        #else:
        #    return self.edge

    def _next_edge_at(self, offset):
        key = self.data_store.value_at(offset)
        node_id = self.node.children_ids[key]
        self._target_edge_length = Node.incoming_edge_length(node_id)
        self._target_start_offset = Node.incoming_edge_start_offset(node_id)
        self._target_node = Node.get(node_id)
        Node.fill(node_id, self.my_edge)
        return self.my_edge

    def next_data_offset(self):
        self.next_edge_offset += 1
        if self.next_edge_offset == self._target_edge_length:
            self.node = self._target_node
            self.next_edge_offset = 0

    def follow_value(self, value):
        """Follow a value to a new location.

        Returns:
            True if the value was followed and Location changed
            False otherwise
        """
        if self.next_edge_offset > 0:
            return self._follow_edge_value(value)
        elif self.node.has_child_value(value):
            return self._locate_after_first_edge_value(value)
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
            edge = self._next_edge_at(offset)
            if self._target_edge_length > amount_to_traverse or self._target_edge_length < 0:
                self.next_edge_offset = amount_to_traverse
            else:
                amount_to_traverse -= self._target_edge_length
                self.skip_count_down(self._target_node, offset + self._target_edge_length, amount_to_traverse)

    def _follow_edge_value(self, value):
        result = self.data_store.value_at(self._target_start_offset + self.next_edge_offset) == value
        if result:
            self.next_data_offset()
        return result

    def _locate_after_first_edge_value(self, value):
        child_node_id = self.node.children_ids[value]
        self._target_edge_length = Node.incoming_edge_length(child_node_id)
        self._target_start_offset = Node.incoming_edge_start_offset(child_node_id)
        if self._target_edge_length == 1:
            self.node = Node.get(child_node_id)
            self.next_edge_offset = 0
        else:
            self.next_edge_offset = 1
            self.value_key = value
            self._target_node = Node.get(child_node_id)

        return True

    def __repr__(self):
        locstr = "on Node"
        if self.next_edge_offset > 0:
            locstr = "on Edge, offset {}".format(self.next_edge_offset)
        return "node({}), {}".format(self.node.id, locstr)



