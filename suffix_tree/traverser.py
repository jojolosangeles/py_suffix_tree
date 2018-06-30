class Traverser:
    def __init__(self, data_store):
        self.data_store = data_store

    """Given a location, moves to a new location."""
    def traverse_by_value(self, location, value):
        """Traverses from current location based on a given value.

        This implementation modifies the location.

        Returns:
            (new location, True) if the traversal succeeds
            (original location, False) if the traversal fails
        """
        if location.on_node:
            if value in location.node.children:
                location.node = location.node.children[value]
                location.data_source_value_offset = location.node.incoming_edge_start_offset
                return (location, True)
        elif value == self.data_store.value_at(location.data_source_value_offset + 1):
            location.data_source_value_offset += 1
            return (location, True)
        return (location, False)

    def traverse_to_next_suffix(self, location):
        """
        Traverse to the suffix for this node.

        Return:
                (new location, True) if the location changed
                (original location, False) if location unchanged
        """
        if location.node.is_root():
            return (location, False)

        next_node = location.node.suffix_link
        if next_node == None:
            # we have no suffix link, traverse up
            amount_to_traverse = location.node.incoming_edge_length
            parent = location.node.parent
            value_offset = location.node.incoming_edge_start_offset
            # the root suffix link is to itself, so we have to manually skip first character
            if parent.is_root():
                value_offset += 1
                amount_to_traverse -= 1
            start_node = parent.suffix_link
            location = self.traverse_down(location, start_node, value_offset, amount_to_traverse)
        else:
            location.node = next_node

        return (location, True)

    def traverse_down(self, location, node, offset, amount_to_traverse):
        if amount_to_traverse == 0:
            location.node = node
            location.data_source_value_offset = node.incoming_edge_end_offset
        else:
            location.node = node.children[self.data_store.value_at(offset)]
            if location.node.is_leaf() or location.node.incoming_edge_length >= amount_to_traverse:
                location.data_source_value_offset = location.node.incoming_edge_start_offset + amount_to_traverse - 1
            else:
                edge_length = location.node.incoming_edge_length
                amount_to_traverse -= edge_length
                return self.traverse_down(location, location.node, offset + edge_length, amount_to_traverse)
        return location