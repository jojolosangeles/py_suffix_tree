from suffix_tree.location import LocationFactory, Location


class Relocate:
    def __init__(self, data_store):
        self.data_store = data_store

    def follow_value(self, location, value):
        """Follow a value to get a new location.

        Returns:
            (newLocation, True) if successful
            (originalLocation, False) otherwise
        """
        if location.on_node:
            if value in location.node.children:
                return (LocationFactory.create(location.node.children[value], location.node.incoming_edge_start_offset), True)
        elif value == self.data_store.value_at(location.data_offset + 1):
            return (LocationFactory.next_data_offset(location), True)
        return (location, False)

    def go_to_suffix(self, location):
        """
        Traverse to the suffix for this node.

        Return:
                (new location, True) if the location changed
                (original location, False) if location unchanged
        """
        if location.node.is_root():
            return location, False

        if location.node.suffix_link == None:
            # When a node does NOT have a suffix link, it is a newly
            # created internal node, and will get its link as the value
            # is processed.  The Ukkonen algorithm guarantees the parent
            # has a suffix link, since at most one node in entire graph
            # is missing a suffix link during processing of a value.
            amount_to_traverse = location.node.incoming_edge_length
            parent = location.node.parent
            value_offset = location.node.incoming_edge_start_offset

            # By definition, suffix links decrease depth in tree by one value
            # except for root, which has itself as a suffix link, in that case
            # we have to manually skip a value.
            if parent.is_root():
                value_offset += 1
                amount_to_traverse -= 1

            return self.traverse_down(location, parent.suffix_link, value_offset, amount_to_traverse), True
        else:
            return LocationFactory.create(location.node.suffix_link, Location.ON_NODE), True

    def traverse_down(self, location, node, offset, amount_to_traverse):
        """Traverse down a node starting at a given offset in the data
        source when the path down is assumed to exist.  This allows
        downward traversal by only checking the first value down.
        """
        if amount_to_traverse == 0:
            return LocationFactory.create(node, Location.ON_NODE)
        else:
            child = node.children[self.data_store.value_at(offset)]
            if child.is_leaf() or child.incoming_edge_length >= amount_to_traverse:
                return LocationFactory.create(child, child.incoming_edge_start_offset + amount_to_traverse - 1)
            else:
                edge_length = child.incoming_edge_length
                amount_to_traverse -= edge_length
                return self.traverse_down(LocationFactory.create(child, Location.ON_NODE),
                                          child, offset + edge_length, amount_to_traverse)