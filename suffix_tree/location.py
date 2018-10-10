"""Location within a suffix tree, as each value in the sequence is processed.

The location is between items in the sequence, so there is 0 (if root)
or more 'previous' values, and one (if on edge) or more 'next' values.

    * NODE (has two outgoing edges)
    value1a * value1b * value1c * NODE
                                  value3a value3b value3c
                                  value4a value4b value4c
    value2a * value2v * NODE

The values are numbers representing the offset within the sequence of values.

Within an edge, each value offset is sequential, so we need only store the first offset
and last offset (or length).

The location also needs the offset of the previous value, since the algorithm needs
to know if the value being processed already exists in the tree.
"""
class Location:

    """A location within a suffix tree, either on a node or on an edge."""
    def __init__(self, node, data_store):
        self.node = node
        self.data_offset = node.incoming_edge_end_offset
        self.on_node = True
        self.data_store = data_store

    def locate_on_node(self, node):
        self.locate_on_edge(node, node.incoming_edge_end_offset)

    def locate_on_edge(self, node, offset):
        self.node = node
        self.data_offset = offset
        self.on_node = self.node.incoming_edge_end_offset == offset

    def next_offset_matches(self, value):
        return self.data_store.value_at(self.data_offset + 1) == value

    def next_node_at(self, offset):
        return self.node.children[self.data_store.value_at(offset)]

    def next_data_offset(self):
        self.data_offset += 1
        self.on_node = self.node.incoming_edge_end_offset == self.data_offset

    def follow_edge_value(self, value):
        result = self.data_store.value_at(self.data_offset + 1) == value
        if result:
            self.next_data_offset()
        return result

    def follow_value(self, value):
        """Follow a value to get a new location.

        Returns:
            True if successfully modified location
            False otherwise
        """
        if self.on_node:
            if value in self.node.children:
                dest_node = self.node.children[value]
                self.locate_on_edge(dest_node, dest_node.incoming_edge_start_offset)
                return True
        elif self.follow_edge_value(value):
            return True
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
            # When a node does NOT have a suffix link, it is a newly
            # created internal node, and will get its link as the value
            # is processed.  The Ukkonen algorithm guarantees the parent
            # has a suffix link, since at most one node in entire graph
            # is missing a suffix link during processing of a value.
            amount_to_traverse = self.node.incoming_edge_length()
            parent = self.node.parent
            value_offset = self.node.incoming_edge_start_offset

            # By definition, suffix links decrease depth in tree by one value
            # except for root, which has itself as a suffix link, in that case
            # we have to manually skip a value.
            if parent.is_root():
                value_offset += 1
                amount_to_traverse -= 1

            self.traverse_down(parent.suffix_link, value_offset, amount_to_traverse)
            return True
        else:
            self.locate_on_node(self.node.suffix_link)
            return True

    def traverse_down(self, node, offset, amount_to_traverse):
        """Traverse down a node starting at a given offset in the data
        source when the path down is assumed to exist (skip/count), so
        we only check first value when traversing edge down.
        """
        self.locate_on_node(node)
        if amount_to_traverse > 0:
            child = self.next_node_at(offset)
            if child.is_leaf() or child.incoming_edge_length() >= amount_to_traverse:
                self.locate_on_edge(child, child.incoming_edge_start_offset + amount_to_traverse - 1)
            else:
                edge_length = child.incoming_edge_length()
                amount_to_traverse -= edge_length
                self.traverse_down(child, offset + edge_length, amount_to_traverse)

    def __repr__(self):
        return "node({}), incoming {}-{}, data_offset {}, on_node={}".\
                format(self.node.id,
                       self.node.incoming_edge_start_offset,
                       self.node.incoming_edge_end_offset,
                       self.data_offset, self.on_node)


