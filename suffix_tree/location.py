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
        self.on_node = True
        self.data_store = data_store

    def locate_on_node(self, node):
        self.node = node
        self.on_node = True
        self.data_offset = 0

    def locate_on_leaf_edge(self, node, offset):
        self.node = node
        self.data_offset = offset
        self.on_node = False

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


    def go_to_suffix(self, nodeStore):
        """
        Traverse to the suffix for this node.

        Return:
                True if the location changed
                False otherwise
        """
        if self.node.is_root():
            return False

        if not hasattr(self.node, 'suffixLink'):
            # When a node does NOT have a suffix link, it is a newly
            # created internal node, and will get its link as the value
            # is processed.  The Ukkonen algorithm guarantees the parent
            # has a suffix link, since at most one node in entire graph
            # is missing a suffix link during processing of a value.
            stringToTraverseDown = self.node.incomingEdgeValueSequence
            parent = self.node.parent
            if parent == parent.suffixLink:
                stringToTraverseDown = stringToTraverseDown[1:]
            suffixLink = parent.suffixLink
            self.traverse_down(nodeStore, suffixLink, stringToTraverseDown)
            return True
        else:
            self.locate_on_node(self.node.suffixLink)
            return True

    def traverse_down(self, nodeStore, node, stringToTraverseDown):
        """Traverse down a node starting at a given offset in the data
        source when the path down is assumed to exist (skip/count), so
        we only check first value when traversing edge down.
        """
        self.locate_on_node(node)
        amount_to_traverse = len(stringToTraverseDown)
        if amount_to_traverse > 0:
            partition = nodeStore.PK_partition[node.PK]
            child = partition[stringToTraverseDown[0]]
            if child.is_leaf():
                self.locate_on_leaf_edge(child, amount_to_traverse)
            elif child.incomingEdgeLength() >= amount_to_traverse:
                self.locate_on_node(child)
                self.on_node = False
                self.data_offset = amount_to_traverse
            else:
                edge_length = child.incomingEdgeLength()
                self.traverse_down(nodeStore, child, stringToTraverseDown[edge_length:])

    def __repr__(self):
        additional = ""
        if not self.on_node:
            additional = f", data_offset: {self.data_offset}"
        return f"{self.node}, on_node: {self.on_node}{additional}"


