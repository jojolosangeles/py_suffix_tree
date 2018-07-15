from suffix_tree_igraph.location import LocationFactory, Location


class Relocate:
    def __init__(self, data_store, tree_graph):
        self.data_store = data_store
        self.tree_graph = tree_graph

    def follow_value(self, location, value):
        """Follow a value to get a new location.

        Returns:
            (newLocation, True) if successful
            (originalLocation, False) otherwise
        """
        if location.on_node:
            # does the node have an edge with the value key?
            found, node_id, incoming_edge_start_offset, incoming_edge_end_offset = self.tree_graph.has_outgoing_edge(location.node_id, value)
            if found is True:
                return LocationFactory.create_at_offset(
                    location, node_id,
                    incoming_edge_start_offset,
                    incoming_edge_start_offset,
                    incoming_edge_end_offset), True
        elif value == self.data_store.value_at(location.data_offset + 1):
            return LocationFactory.next_data_offset(location), True
        return location, False

    def go_to_suffix(self, location):
        """
        Traverse to the suffix for this node.

        Return:
                (new location, True) if the location changed
                (original location, False) if location unchanged
        """
        if self.tree_graph.is_root(location.node_id):
            return location, False

        suffix_link_id, incoming_edge_start_offset, incoming_edge_end_offset = self.tree_graph.get_suffix_link(location.node_id)
        if suffix_link_id is None:
            # When a node does NOT have a suffix link, it is a newly
            # created internal node, and will get its link as the value
            # is processed.  The Ukkonen algorithm guarantees the parent
            # has a suffix link, since at most one node in entire graph
            # is missing a suffix link during processing of a value.
            amount_to_traverse = location.incoming_edge_length()
            parent_id = self.tree_graph.get_parent(location.node_id)
            value_offset = location.start_offset

            # By definition, suffix links decrease depth in tree by one value,
            # except for root.  Root's suffix link is to itself, so we
            # have to manually skip the value before traversing back down
            if self.tree_graph.is_root(parent_id):
                value_offset += 1
                amount_to_traverse -= 1
            suffix_link_id, _, _ = self.tree_graph.get_suffix_link(parent_id)
            return self.skip_count_traverse_down(location, suffix_link_id, value_offset, amount_to_traverse), True
        else:
            return LocationFactory.create_on_node(location, suffix_link_id, incoming_edge_start_offset, incoming_edge_end_offset), True

    def skip_count_traverse_down(self, location, node_id, offset, amount_to_traverse):
        """Traverse down a node starting at a given offset in the data
        source when the path down is assumed to exist (skip/count), so
        we only check first value when traversing edge down.
        """
        if amount_to_traverse == 0:
            incoming_edge_start_offset, incoming_edge_end_offset = (-1,-1) if self.tree_graph.is_root(node_id) else self.tree_graph.get_incoming_edge_offsets(node_id)
            return LocationFactory.create_on_node(location, node_id, incoming_edge_start_offset, incoming_edge_end_offset)
        else:
            found, child_id, incoming_edge_start_offset, incoming_edge_end_offset = self.tree_graph.has_outgoing_edge(node_id, self.data_store.value_at(offset))
            child_is_leaf = incoming_edge_start_offset > incoming_edge_end_offset
            child_incoming_edge_length = incoming_edge_end_offset - incoming_edge_start_offset + 1
            if child_is_leaf or child_incoming_edge_length >= amount_to_traverse:
                incoming_edge_start_offset, incoming_edge_end_offset = self.tree_graph.get_incoming_edge_offsets(child_id)
                return LocationFactory.create_at_offset(
                    location, child_id,
                    incoming_edge_start_offset + amount_to_traverse - 1,
                    incoming_edge_start_offset, incoming_edge_end_offset)
            else:
                amount_to_traverse -= child_incoming_edge_length
                return self.skip_count_traverse_down(LocationFactory.create_on_node(location, child_id, incoming_edge_start_offset, incoming_edge_end_offset),
                                                     child_id, offset + child_incoming_edge_length,
                                                     amount_to_traverse)