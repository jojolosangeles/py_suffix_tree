from suffix_tree_igraph.igraph_adapter import igraph_has_outgoing_edge, igraph_parent_id, igraph_get_suffix_link, \
    igraph_get_incoming_edge_start_offset, igraph_get_incoming_edge_length, igraph_is_root, igraph_is_leaf
from suffix_tree_igraph.location import LocationFactory, Location


class Relocate:
    def __init__(self, data_store, node_factory):
        self.data_store = data_store
        self.node_factory = node_factory

    def follow_value(self, location, value):
        """Follow a value to get a new location.

        Returns:
            (newLocation, True) if successful
            (originalLocation, False) otherwise
        """
        if location.on_node:
            # does the node have an edge with the value key?
            found,node_id = igraph_has_outgoing_edge(location.node_id, value)
            if found is True:
                incoming_edge_start_offset = igraph_get_incoming_edge_start_offset(node_id)
                return LocationFactory.create(location, node_id, incoming_edge_start_offset), True
        elif value == self.data_store.value_at(location.data_offset + 1):
            return LocationFactory.next_data_offset(location), True
        return location, False

    def go_to_suffix(self, location, node_factory):
        """
        Traverse to the suffix for this node.

        Return:
                (new location, True) if the location changed
                (original location, False) if location unchanged
        """
        if igraph_is_root(location.node_id):
            return location, False

        suffix_link_id = igraph_get_suffix_link(location.node_id)
        if suffix_link_id is None:
            # When a node does NOT have a suffix link, it is a newly
            # created internal node, and will get its link as the value
            # is processed.  The Ukkonen algorithm guarantees the parent
            # has a suffix link, since at most one node in entire graph
            # is missing a suffix link during processing of a value.
            amount_to_traverse = igraph_get_incoming_edge_length(location.node_id)
            parent_id = igraph_parent_id(location.node_id)
            value_offset = igraph_get_incoming_edge_start_offset(location.node_id)

            # By definition, suffix links decrease depth in tree by one value,
            # except for root.  Root's suffix link is to itself, so we
            # have to manually skip the value before traversing back down
            if igraph_is_root(parent_id):
                value_offset += 1
                amount_to_traverse -= 1
            suffix_link_id = igraph_get_suffix_link(parent_id)
            return self.traverse_down(location, suffix_link_id, value_offset, amount_to_traverse, node_factory), True
        else:
            return LocationFactory.create_on_node(location, suffix_link_id), True

    def traverse_down(self, location, node_id, offset, amount_to_traverse, node_factory):
        """Traverse down a node starting at a given offset in the data
        source when the path down is assumed to exist (skip/count), so
        we only check first value when traversing edge down.
        :param node_factory:
        :param amount_to_traverse:
        :param offset:
        :param node:
        :param location:
        """
        if amount_to_traverse == 0:
            return LocationFactory.create_on_node(location, node_id)
        else:
            found,child_id = igraph_has_outgoing_edge(node_id, self.data_store.value_at(offset))
            child_is_leaf = igraph_is_leaf(child_id)
            child_incoming_edge_length = igraph_get_incoming_edge_length(child_id)
            if child_is_leaf or child_incoming_edge_length >= amount_to_traverse:
                incoming_edge_start_offset = igraph_get_incoming_edge_start_offset(child_id)
                return LocationFactory.create(location, child_id, incoming_edge_start_offset + amount_to_traverse - 1)
            else:
                amount_to_traverse -= child_incoming_edge_length
                return self.traverse_down(LocationFactory.create_on_node(location, child_id), child_id, offset + child_incoming_edge_length,
                                          amount_to_traverse, node_factory)