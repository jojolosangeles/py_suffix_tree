class Relocate:
    def __init__(self, data_store):
        self.data_store = data_store

    def follow_value(self, location, value):
        """Follow a value to get a new location.

        Returns:
            True if successfully modified location
            False otherwise
        """
        if location.on_node:
            if value in location.node.children:
                dest_node = location.node.children[value]
                location.locate_on_edge(dest_node, dest_node.incoming_edge_start_offset)
                return True
        elif value == self.data_store.value_at(location.data_offset + 1):
            location.next_data_offset()
            return True
        return False

    def go_to_suffix(self, location):
        """
        Traverse to the suffix for this node.

        Return:
                True if the location changed
                False otherwise
        """
        if location.node.is_root():
            return False

        if location.node.suffix_link is None:
            # When a node does NOT have a suffix link, it is a newly
            # created internal node, and will get its link as the value
            # is processed.  The Ukkonen algorithm guarantees the parent
            # has a suffix link, since at most one node in entire graph
            # is missing a suffix link during processing of a value.
            amount_to_traverse = location.node.incoming_edge_length()
            parent = location.node.parent
            value_offset = location.node.incoming_edge_start_offset

            # By definition, suffix links decrease depth in tree by one value
            # except for root, which has itself as a suffix link, in that case
            # we have to manually skip a value.
            if parent.is_root():
                value_offset += 1
                amount_to_traverse -= 1

            self.traverse_down(location, parent.suffix_link, value_offset, amount_to_traverse)
            return True
        else:
            location.locate_on_node(location.node.suffix_link)
            return True

    def traverse_down(self, location, node, offset, amount_to_traverse):
        """Traverse down a node starting at a given offset in the data
        source when the path down is assumed to exist (skip/count), so
        we only check first value when traversing edge down.
        """
        if amount_to_traverse == 0:
            location.locate_on_node(node)
        else:
            child = node.children[self.data_store.value_at(offset)]
            if child.is_leaf() or child.incoming_edge_length() >= amount_to_traverse:
                location.locate_on_edge(child, child.incoming_edge_start_offset + amount_to_traverse - 1)
            else:
                edge_length = child.incoming_edge_length()
                amount_to_traverse -= edge_length
                location.locate_on_node(child)
                self.traverse_down(location, child, offset + edge_length, amount_to_traverse)