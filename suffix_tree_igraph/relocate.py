from suffix_tree_igraph.igraph_adapter import igraph_has_outgoing_edge, igraph_parent_id
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
            found,node_id = igraph_has_outgoing_edge(location.node.id, value)
            if found is True:
                dest_node = self.node_factory.get_node_by_id(node_id)
                return LocationFactory.create(location, dest_node, dest_node.incoming_edge_start_offset), True
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
        if location.node.is_root():
            return location, False

        if location.node.suffix_link is None:
            # When a node does NOT have a suffix link, it is a newly
            # created internal node, and will get its link as the value
            # is processed.  The Ukkonen algorithm guarantees the parent
            # has a suffix link, since at most one node in entire graph
            # is missing a suffix link during processing of a value.
            amount_to_traverse = location.node.incoming_edge_length()
            parent_id = igraph_parent_id(location.node.id)
            parent = node_factory.get_node_by_id(parent_id)
            value_offset = location.node.incoming_edge_start_offset

            # By definition, suffix links decrease depth in tree by one value
            # except for root, which has itself as a suffix link, in that case
            # we have to manually skip a value.
            if parent.is_root():
                value_offset += 1
                amount_to_traverse -= 1

            return self.traverse_down(location, parent.suffix_link, value_offset, amount_to_traverse, node_factory), True
        else:
            return LocationFactory.createOnNode(location, location.node.suffix_link), True

    def traverse_down(self, location, node, offset, amount_to_traverse, node_factory):
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
            return LocationFactory.createOnNode(location, node)
        else:
            found,node_id = igraph_has_outgoing_edge(node.id, self.data_store.value_at(offset))
            child = node_factory.get_node_by_id(node_id)
            if child.is_leaf() or child.incoming_edge_length() >= amount_to_traverse:
                return LocationFactory.create(location, child, child.incoming_edge_start_offset + amount_to_traverse - 1)
            else:
                edge_length = child.incoming_edge_length()
                amount_to_traverse -= edge_length
                return self.traverse_down(LocationFactory.createOnNode(location, child), child, offset + edge_length,
                                          amount_to_traverse, )